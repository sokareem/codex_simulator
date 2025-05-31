"""
MCP Client Implementation
Client adapter for routing tool calls and context requests through MCP server.
"""

import asyncio
import json
import uuid
import aiohttp
import websockets
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from .schemas import (
    MCPMessage, MCPToolInvocationRequest, MCPToolInvocationResponse,
    MCPContextFetchRequest, MCPContextFetchResponse,
    MCPStateUpdateRequest, MCPStateUpdateResponse,
    MCPErrorResponse, MCPHeartbeatMessage,
    MCPConnectionConfig, validate_mcp_message
)

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client for communicating with MCP server"""
    
    def __init__(self, config: MCPConnectionConfig, agent_id: str):
        self.config = config
        self.agent_id = agent_id
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.heartbeat_task: Optional[asyncio.Task] = None
        self._response_futures: Dict[str, asyncio.Future] = {}
        
    async def connect(self, use_websocket: bool = True):
        """Connect to MCP server"""
        try:
            if use_websocket:
                await self._connect_websocket()
            else:
                await self._connect_http()
            
            self.is_connected = True
            logger.info(f"MCP Client {self.agent_id} connected to {self.config.server_url}")
            
            # Start heartbeat if using WebSocket
            if use_websocket and self.websocket:
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self.is_connected = False
        
        # Cancel heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info(f"MCP Client {self.agent_id} disconnected")
    
    async def _connect_websocket(self):
        """Connect via WebSocket"""
        ws_url = self.config.server_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/{self.agent_id}"
        
        self.websocket = await websockets.connect(ws_url)
        
        # Start message handler
        asyncio.create_task(self._websocket_message_handler())
    
    async def _connect_http(self):
        """Connect via HTTP"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        headers = {}
        
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
    
    async def _websocket_message_handler(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                if message.type == websockets.MessageType.TEXT:
                    try:
                        data = json.loads(message.data)
                        response = validate_mcp_message(data)
                        
                        # Handle response to pending request
                        request_id = getattr(response, 'request_id', None)
                        if request_id and request_id in self._response_futures:
                            future = self._response_futures.pop(request_id)
                            if not future.done():
                                future.set_result(response)
                        
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"WebSocket message handler error: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        try:
            while self.is_connected and self.websocket:
                heartbeat = MCPHeartbeatMessage(
                    agent_id=self.agent_id,
                    status="active"
                )
                
                await self.websocket.send(heartbeat.json())
                await asyncio.sleep(self.config.heartbeat_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
    
    async def invoke_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> MCPToolInvocationResponse:
        """Invoke a tool through MCP server"""
        
        request = MCPToolInvocationRequest(
            request_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            tool_name=tool_name,
            arguments=arguments,
            context=context,
            timeout=timeout or self.config.timeout
        )
        
        if self.websocket:
            return await self._send_websocket_request(request)
        else:
            return await self._send_http_request("/invoke_tool", request)
    
    async def fetch_context(
        self,
        context_keys: List[str],
        scope: str = "session"
    ) -> MCPContextFetchResponse:
        """Fetch context data from MCP server"""
        
        request = MCPContextFetchRequest(
            request_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            context_keys=context_keys,
            scope=scope
        )
        
        if self.websocket:
            return await self._send_websocket_request(request)
        else:
            return await self._send_http_request("/fetch_context", request)
    
    async def update_state(
        self,
        state_updates: Dict[str, Any],
        scope: str = "session",
        merge_strategy: str = "merge"
    ) -> MCPStateUpdateResponse:
        """Update state through MCP server"""
        
        request = MCPStateUpdateRequest(
            request_id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            state_updates=state_updates,
            scope=scope,
            merge_strategy=merge_strategy
        )
        
        if self.websocket:
            return await self._send_websocket_request(request)
        else:
            return await self._send_http_request("/update_state", request)
    
    async def _send_websocket_request(self, request: MCPMessage) -> MCPMessage:
        """Send request via WebSocket and wait for response"""
        if not self.websocket:
            raise ConnectionError("WebSocket not connected")
        
        # Create future for response
        future = asyncio.Future()
        self._response_futures[request.request_id] = future
        
        try:
            # Send request
            await self.websocket.send(request.json())
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=self.config.timeout)
            return response
            
        except asyncio.TimeoutError:
            self._response_futures.pop(request.request_id, None)
            raise TimeoutError(f"Request {request.request_id} timed out")
        except Exception as e:
            self._response_futures.pop(request.request_id, None)
            raise
    
    async def _send_http_request(self, endpoint: str, request: MCPMessage) -> MCPMessage:
        """Send request via HTTP"""
        if not self.session:
            raise ConnectionError("HTTP session not initialized")
        
        url = f"{self.config.server_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.post(url, json=request.dict()) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return validate_mcp_message(data)
                    
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    raise
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)

class MCPToolWrapper:
    """Wrapper to route tool calls through MCP client"""
    
    def __init__(self, tool_name: str, mcp_client: MCPClient):
        self.tool_name = tool_name
        self.mcp_client = mcp_client
        self.name = tool_name  # For compatibility with CrewAI tools
        self.description = f"MCP-wrapped tool: {tool_name}"
    
    async def __call__(self, *args, **kwargs) -> Any:
        """Execute tool through MCP client"""
        # Convert args to kwargs if needed
        arguments = kwargs.copy()
        if args:
            arguments["_args"] = list(args)
        
        response = await self.mcp_client.invoke_tool(
            tool_name=self.tool_name,
            arguments=arguments
        )
        
        if response.success:
            return response.result
        else:
            raise RuntimeError(f"Tool execution failed: {response.error_message}")
    
    def _run(self, *args, **kwargs) -> Any:
        """Synchronous wrapper for CrewAI compatibility"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, create a new task
            task = asyncio.create_task(self.__call__(*args, **kwargs))
            return asyncio.run_coroutine_threadsafe(task, loop).result()
        else:
            return loop.run_until_complete(self.__call__(*args, **kwargs))

class MCPClientPool:
    """Pool of MCP clients for load balancing"""
    
    def __init__(self, configs: List[MCPConnectionConfig], agent_id_prefix: str = "agent"):
        self.configs = configs
        self.agent_id_prefix = agent_id_prefix
        self.clients: List[MCPClient] = []
        self.current_index = 0
    
    async def initialize(self):
        """Initialize all clients in the pool"""
        for i, config in enumerate(self.configs):
            agent_id = f"{self.agent_id_prefix}-{i}"
            client = MCPClient(config, agent_id)
            await client.connect()
            self.clients.append(client)
    
    async def cleanup(self):
        """Cleanup all clients"""
        for client in self.clients:
            await client.disconnect()
        self.clients.clear()
    
    def get_client(self) -> MCPClient:
        """Get next available client (round-robin)"""
        if not self.clients:
            raise RuntimeError("No clients available in pool")
        
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
    
    @asynccontextmanager
    async def get_client_context(self):
        """Get client with automatic cleanup"""
        client = self.get_client()
        try:
            yield client
        finally:
            # Client cleanup handled by pool
            pass

# Convenience functions
async def create_mcp_client(server_url: str, agent_id: str, **kwargs) -> MCPClient:
    """Create and connect MCP client"""
    config = MCPConnectionConfig(
        server_url=server_url,
        client_id=agent_id,
        **kwargs
    )
    
    client = MCPClient(config, agent_id)
    await client.connect()
    return client

def wrap_tools_with_mcp(tool_names: List[str], mcp_client: MCPClient) -> List[MCPToolWrapper]:
    """Wrap multiple tools with MCP client"""
    return [MCPToolWrapper(name, mcp_client) for name in tool_names]

"""
MCP Server Implementation
Async HTTP and WebSocket server for Model Context Protocol communication.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .schemas import (
    MCPMessage, MCPToolInvocationRequest, MCPToolInvocationResponse,
    MCPContextFetchRequest, MCPContextFetchResponse,
    MCPStateUpdateRequest, MCPStateUpdateResponse,
    MCPErrorResponse, MCPHeartbeatMessage, MCPServerInfo,
    MCPConnectionConfig, validate_mcp_message, MCP_VERSION
)

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation with HTTP and WebSocket support"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.context_store: Dict[str, Dict[str, Any]] = {
            "global": {},
            "session": {},
            "agent": {}
        }
        self.tool_registry: Dict[str, Callable] = {}
        self.server_id = f"mcp-server-{uuid.uuid4().hex[:8]}"
        
        # Create FastAPI app
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info(f"MCP Server {self.server_id} starting up...")
            yield
            # Shutdown
            logger.info(f"MCP Server {self.server_id} shutting down...")
            await self._cleanup_connections()
        
        app = FastAPI(
            title="MCP Server",
            description="Model Context Protocol Server for CodexSimulator",
            version=MCP_VERSION,
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routes
        self._add_routes(app)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add HTTP and WebSocket routes"""
        
        @app.get("/")
        async def root():
            return {"message": "MCP Server is running", "server_id": self.server_id}
        
        @app.get("/info", response_model=MCPServerInfo)
        async def server_info():
            return MCPServerInfo(
                server_id=self.server_id,
                version=MCP_VERSION,
                capabilities=["tool_invocation", "context_management", "state_updates"],
                supported_tools=list(self.tool_registry.keys()),
                max_concurrent_requests=10
            )
        
        @app.post("/invoke_tool")
        async def invoke_tool_http(request: MCPToolInvocationRequest):
            """HTTP endpoint for tool invocation"""
            try:
                response = await self._handle_tool_invocation(request)
                return response.dict()
            except Exception as e:
                logger.error(f"Tool invocation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/fetch_context")
        async def fetch_context_http(request: MCPContextFetchRequest):
            """HTTP endpoint for context fetching"""
            try:
                response = await self._handle_context_fetch(request)
                return response.dict()
            except Exception as e:
                logger.error(f"Context fetch error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/update_state")
        async def update_state_http(request: MCPStateUpdateRequest):
            """HTTP endpoint for state updates"""
            try:
                response = await self._handle_state_update(request)
                return response.dict()
            except Exception as e:
                logger.error(f"State update error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.websocket("/ws/{agent_id}")
        async def websocket_endpoint(websocket: WebSocket, agent_id: str):
            """WebSocket endpoint for real-time communication"""
            await self._handle_websocket_connection(websocket, agent_id)
    
    async def _handle_websocket_connection(self, websocket: WebSocket, agent_id: str):
        """Handle WebSocket connection lifecycle"""
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        
        try:
            # Register agent
            self.agent_registry[agent_id] = {
                "connected_at": datetime.now(),
                "status": "active",
                "last_heartbeat": datetime.now()
            }
            
            logger.info(f"Agent {agent_id} connected via WebSocket")
            
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Validate and process message
                try:
                    message = validate_mcp_message(message_data)
                    response = await self._process_message(message, agent_id)
                    
                    if response:
                        await websocket.send_text(response.json())
                        
                except Exception as e:
                    error_response = MCPErrorResponse(
                        request_id=message_data.get("request_id", "unknown"),
                        error_code="PROCESSING_ERROR",
                        error_message=str(e)
                    )
                    await websocket.send_text(error_response.json())
                    
        except WebSocketDisconnect:
            logger.info(f"Agent {agent_id} disconnected")
        except Exception as e:
            logger.error(f"WebSocket error for agent {agent_id}: {e}")
        finally:
            # Cleanup
            if agent_id in self.active_connections:
                del self.active_connections[agent_id]
            if agent_id in self.agent_registry:
                del self.agent_registry[agent_id]
    
    async def _process_message(self, message: MCPMessage, agent_id: str) -> Optional[MCPMessage]:
        """Process incoming MCP message and return response"""
        
        if isinstance(message, MCPToolInvocationRequest):
            return await self._handle_tool_invocation(message)
        elif isinstance(message, MCPContextFetchRequest):
            return await self._handle_context_fetch(message)
        elif isinstance(message, MCPStateUpdateRequest):
            return await self._handle_state_update(message)
        elif isinstance(message, MCPHeartbeatMessage):
            return await self._handle_heartbeat(message, agent_id)
        else:
            logger.warning(f"Unhandled message type: {type(message)}")
            return None
    
    async def _handle_tool_invocation(self, request: MCPToolInvocationRequest) -> MCPToolInvocationResponse:
        """Handle tool invocation request"""
        start_time = datetime.now()
        
        try:
            tool_name = request.tool_name
            if tool_name not in self.tool_registry:
                raise ValueError(f"Tool '{tool_name}' not found in registry")
            
            tool_func = self.tool_registry[tool_name]
            
            # Execute tool with timeout
            try:
                if asyncio.iscoroutinefunction(tool_func):
                    result = await asyncio.wait_for(
                        tool_func(**request.arguments),
                        timeout=request.timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: tool_func(**request.arguments)
                        ),
                        timeout=request.timeout
                    )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return MCPToolInvocationResponse(
                    request_id=request.request_id,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    metadata={
                        "tool_name": tool_name,
                        "agent_id": request.agent_id
                    }
                )
                
            except asyncio.TimeoutError:
                raise ValueError(f"Tool execution timed out after {request.timeout} seconds")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Tool invocation failed: {e}")
            
            return MCPToolInvocationResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def _handle_context_fetch(self, request: MCPContextFetchRequest) -> MCPContextFetchResponse:
        """Handle context fetch request"""
        try:
            context_data = {}
            missing_keys = []
            
            scope_store = self.context_store.get(request.scope, {})
            
            for key in request.context_keys:
                if request.scope == "agent":
                    full_key = f"{request.agent_id}.{key}"
                    if full_key in scope_store:
                        context_data[key] = scope_store[full_key]
                    else:
                        missing_keys.append(key)
                else:
                    if key in scope_store:
                        context_data[key] = scope_store[key]
                    else:
                        missing_keys.append(key)
            
            return MCPContextFetchResponse(
                request_id=request.request_id,
                success=True,
                context_data=context_data,
                missing_keys=missing_keys
            )
            
        except Exception as e:
            logger.error(f"Context fetch failed: {e}")
            return MCPContextFetchResponse(
                request_id=request.request_id,
                success=False,
                context_data={},
                missing_keys=request.context_keys
            )
    
    async def _handle_state_update(self, request: MCPStateUpdateRequest) -> MCPStateUpdateResponse:
        """Handle state update request"""
        try:
            updated_keys = []
            scope_store = self.context_store.setdefault(request.scope, {})
            
            for key, value in request.state_updates.items():
                if request.scope == "agent":
                    full_key = f"{request.agent_id}.{key}"
                else:
                    full_key = key
                
                if request.merge_strategy == "replace":
                    scope_store[full_key] = value
                elif request.merge_strategy == "merge" and isinstance(value, dict):
                    if full_key in scope_store and isinstance(scope_store[full_key], dict):
                        scope_store[full_key].update(value)
                    else:
                        scope_store[full_key] = value
                elif request.merge_strategy == "append" and isinstance(value, list):
                    if full_key in scope_store and isinstance(scope_store[full_key], list):
                        scope_store[full_key].extend(value)
                    else:
                        scope_store[full_key] = value
                else:
                    scope_store[full_key] = value
                
                updated_keys.append(key)
            
            return MCPStateUpdateResponse(
                request_id=request.request_id,
                success=True,
                updated_keys=updated_keys
            )
            
        except Exception as e:
            logger.error(f"State update failed: {e}")
            return MCPStateUpdateResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e)
            )
    
    async def _handle_heartbeat(self, message: MCPHeartbeatMessage, agent_id: str) -> None:
        """Handle heartbeat message"""
        if agent_id in self.agent_registry:
            self.agent_registry[agent_id].update({
                "status": message.status,
                "last_heartbeat": message.timestamp,
                "load_metrics": message.load_metrics
            })
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool function"""
        self.tool_registry[name] = func
        logger.info(f"Registered tool: {name}")
    
    def unregister_tool(self, name: str):
        """Unregister a tool function"""
        if name in self.tool_registry:
            del self.tool_registry[name]
            logger.info(f"Unregistered tool: {name}")
    
    async def broadcast_message(self, message: MCPMessage, exclude_agents: Optional[Set[str]] = None):
        """Broadcast message to all connected agents"""
        exclude_agents = exclude_agents or set()
        
        for agent_id, websocket in self.active_connections.items():
            if agent_id not in exclude_agents:
                try:
                    await websocket.send_text(message.json())
                except Exception as e:
                    logger.error(f"Failed to send message to agent {agent_id}: {e}")
    
    async def _cleanup_connections(self):
        """Cleanup all active connections"""
        for agent_id, websocket in self.active_connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing connection for agent {agent_id}: {e}")
        
        self.active_connections.clear()
        self.agent_registry.clear()
    
    async def start(self):
        """Start the MCP server"""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

# Convenience function to create and run server
async def run_mcp_server(host: str = "localhost", port: int = 8000, **kwargs):
    """Run MCP server with default configuration"""
    server = MCPServer(host, port)
    
    # Register any additional tools passed in kwargs
    for tool_name, tool_func in kwargs.get("tools", {}).items():
        server.register_tool(tool_name, tool_func)
    
    await server.start()

if __name__ == "__main__":
    asyncio.run(run_mcp_server())

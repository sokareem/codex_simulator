import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from ..mcp import (
    MCPServer, MCPClient, MCPToolWrapper, MCPConnectionConfig,
    MCPToolInvocationRequest, MCPToolInvocationResponse,
    validate_mcp_message
)
from ..mcp.server import run_mcp_server
from ..mcp.client import create_mcp_client, wrap_tools_with_mcp

@pytest.fixture
async def mcp_server():
    """Create test MCP server"""
    server = MCPServer(host="localhost", port=8001)
    
    # Register test tools
    def test_tool(message: str) -> str:
        return f"Processed: {message}"
    
    async def async_test_tool(data: dict) -> dict:
        await asyncio.sleep(0.1)  # Simulate work
        return {"result": f"Async processed: {data}"}
    
    server.register_tool("test_tool", test_tool)
    server.register_tool("async_test_tool", async_test_tool)
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait a moment for server to start
    await asyncio.sleep(0.5)
    
    yield server
    
    # Cleanup
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest.fixture
async def mcp_client(mcp_server):
    """Create test MCP client"""
    config = MCPConnectionConfig(
        server_url="http://localhost:8001",
        client_id="test_client",
        timeout=10
    )
    
    client = MCPClient(config, "test_agent")
    await client.connect(use_websocket=False)  # Use HTTP for testing
    
    yield client
    
    await client.disconnect()

class TestMCPSchemas:
    """Test MCP message schemas and validation"""
    
    def test_tool_invocation_request_validation(self):
        """Test tool invocation request schema"""
        request_data = {
            "message_type": "invoke_tool",
            "request_id": "test-123",
            "agent_id": "test_agent",
            "tool_name": "test_tool",
            "arguments": {"message": "hello"},
            "priority": 5,
            "timeout": 30
        }
        
        request = validate_mcp_message(request_data)
        assert isinstance(request, MCPToolInvocationRequest)
        assert request.tool_name == "test_tool"
        assert request.arguments == {"message": "hello"}
    
    def test_invalid_message_type(self):
        """Test validation with invalid message type"""
        invalid_data = {
            "message_type": "invalid_type",
            "request_id": "test-123"
        }
        
        with pytest.raises(ValueError, match="Unsupported message type"):
            validate_mcp_message(invalid_data)

class TestMCPServer:
    """Test MCP server functionality"""
    
    @pytest.mark.asyncio
    async def test_server_tool_registration(self, mcp_server):
        """Test tool registration and listing"""
        assert "test_tool" in mcp_server.tool_registry
        assert "async_test_tool" in mcp_server.tool_registry
        
        # Test tool unregistration
        mcp_server.unregister_tool("test_tool")
        assert "test_tool" not in mcp_server.tool_registry
    
    @pytest.mark.asyncio
    async def test_server_context_management(self, mcp_server):
        """Test server context storage and retrieval"""
        # Test context update
        await mcp_server._handle_state_update(Mock(
            request_id="test-update",
            agent_id="test_agent",
            state_updates={"key1": "value1", "key2": {"nested": "data"}},
            scope="session",
            merge_strategy="merge"
        ))
        
        # Verify context was stored
        assert "key1" in mcp_server.context_store["session"]
        assert mcp_server.context_store["session"]["key1"] == "value1"

class TestMCPClient:
    """Test MCP client functionality"""
    
    @pytest.mark.asyncio
    async def test_client_tool_invocation(self, mcp_client):
        """Test client tool invocation"""
        response = await mcp_client.invoke_tool(
            tool_name="test_tool",
            arguments={"message": "test message"}
        )
        
        assert response.success is True
        assert "Processed: test message" in str(response.result)
    
    @pytest.mark.asyncio
    async def test_client_context_operations(self, mcp_client):
        """Test client context fetch and update"""
        # Update context
        update_response = await mcp_client.update_state(
            state_updates={"test_key": "test_value"},
            scope="session"
        )
        assert update_response.success is True
        
        # Fetch context
        fetch_response = await mcp_client.fetch_context(
            context_keys=["test_key"],
            scope="session"
        )
        assert fetch_response.success is True
        assert fetch_response.context_data.get("test_key") == "test_value"
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self, mcp_client):
        """Test client error handling for invalid tools"""
        response = await mcp_client.invoke_tool(
            tool_name="nonexistent_tool",
            arguments={}
        )
        
        assert response.success is False
        assert "not found" in response.error_message.lower()

class TestMCPToolWrapper:
    """Test MCP tool wrapper functionality"""
    
    @pytest.mark.asyncio
    async def test_tool_wrapper_execution(self, mcp_client):
        """Test MCP tool wrapper execution"""
        wrapper = MCPToolWrapper("test_tool", mcp_client)
        
        result = await wrapper(message="wrapped test")
        assert "Processed: wrapped test" in str(result)
    
    def test_tool_wrapper_sync_execution(self, mcp_client):
        """Test synchronous execution wrapper"""
        wrapper = MCPToolWrapper("test_tool", mcp_client)
        
        # Test _run method for CrewAI compatibility
        result = wrapper._run(message="sync test")
        assert "Processed: sync test" in str(result)

class TestMCPIntegration:
    """Test MCP integration with CodexSimulator components"""
    
    @pytest.mark.asyncio
    async def test_crew_factory_mcp_integration(self):
        """Test crew factory with MCP integration"""
        from ..flows.crew_factories import CrewFactory
        
        # Mock MCP client
        mock_mcp_client = AsyncMock()
        mock_mcp_client.agent_id = "test_agent"
        
        # Create crew factory with MCP
        factory = CrewFactory(
            llm=Mock(),
            use_mcp=True,
            mcp_client=mock_mcp_client
        )
        
        context = {"command": "test command", "cwd": "/test"}
        crew = factory.create_file_crew(context)
        
        # Verify crew was created
        assert crew is not None
        assert len(crew.agents) == 1
    
    @patch('codex_simulator.mcp.client.create_mcp_client')
    @pytest.mark.asyncio 
    async def test_codex_simulator_mcp_initialization(self, mock_create_client):
        """Test CodexSimulator MCP initialization"""
        from ..crew import CodexSimulator
        
        # Mock successful MCP client creation
        mock_client = AsyncMock()
        mock_create_client.return_value = mock_client
        
        # Initialize simulator with MCP
        simulator = CodexSimulator(use_mcp=True, mcp_server_url="http://test:8000")
        
        # Wait for async initialization
        await asyncio.sleep(0.1)
        
        # Verify MCP client was created
        mock_create_client.assert_called_once_with(
            server_url="http://test:8000",
            agent_id="codex_simulator_main",
            timeout=30
        )

class TestMCPDelegateTool:
    """Test MCP-enabled delegation tool"""
    
    @pytest.mark.asyncio
    async def test_mcp_delegation_tool(self):
        """Test MCP delegation tool functionality"""
        from ..tools.delegate_tool import MCPDelegateTool
        
        # Mock MCP client
        mock_mcp_client = AsyncMock()
        mock_response = Mock()
        mock_response.success = True
        mock_response.result = "Task completed successfully"
        mock_mcp_client.invoke_tool.return_value = mock_response
        
        # Create delegation tool
        agents_dict = {"TestAgent": Mock()}
        delegate_tool = MCPDelegateTool(
            agents_dict=agents_dict,
            mcp_client=mock_mcp_client
        )
        
        # Test delegation
        result = delegate_tool._run(
            task="test task",
            coworker="TestAgent", 
            context="test context"
        )
        
        assert "Task completed successfully" in result
    
    @pytest.mark.asyncio
    async def test_mcp_delegation_fallback(self):
        """Test fallback to direct delegation when MCP fails"""
        from ..tools.delegate_tool import MCPDelegateTool
        
        # Mock agent with execute method
        mock_agent = Mock()
        mock_agent.execute.return_value = "Direct execution result"
        
        agents_dict = {"TestAgent": mock_agent}
        delegate_tool = MCPDelegateTool(
            agents_dict=agents_dict,
            mcp_client=None  # No MCP client
        )
        
        result = delegate_tool._run(
            task="test task",
            coworker="TestAgent",
            context="test context"
        )
        
        assert "Direct execution result" in result

if __name__ == "__main__":
    pytest.main([__file__])

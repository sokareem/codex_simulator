"""
Model Context Protocol (MCP) Integration Module

This module provides MCP server and client implementations for dynamic tool access,
context sharing, and unified message routing across agents in the CodexSimulator.
"""

from .schemas import (
    MCPMessage, MCPToolInvocationRequest, MCPToolInvocationResponse,
    MCPContextFetchRequest, MCPContextFetchResponse,
    MCPStateUpdateRequest, MCPStateUpdateResponse,
    MCPErrorResponse, MCPHeartbeatMessage,
    MCPConnectionConfig, MCPServerInfo,
    validate_mcp_message, MCP_VERSION
)

from .server import MCPServer, run_mcp_server
from .client import MCPClient, MCPToolWrapper, MCPClientPool, create_mcp_client, wrap_tools_with_mcp

__all__ = [
    # Schemas
    'MCPMessage', 'MCPToolInvocationRequest', 'MCPToolInvocationResponse',
    'MCPContextFetchRequest', 'MCPContextFetchResponse',
    'MCPStateUpdateRequest', 'MCPStateUpdateResponse',
    'MCPErrorResponse', 'MCPHeartbeatMessage',
    'MCPConnectionConfig', 'MCPServerInfo',
    'validate_mcp_message', 'MCP_VERSION',
    
    # Server
    'MCPServer', 'run_mcp_server',
    
    # Client
    'MCPClient', 'MCPToolWrapper', 'MCPClientPool',
    'create_mcp_client', 'wrap_tools_with_mcp'
]

# Version information
__version__ = MCP_VERSION

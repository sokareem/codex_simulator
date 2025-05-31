"""
MCP Communication Schemas and Contracts
Defines the JSON/RPC schemas for tool invocation, context sharing, and state management.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Version information
MCP_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"

class MCPMessageType(str, Enum):
    """Types of MCP messages"""
    INVOKE_TOOL = "invoke_tool"
    FETCH_CONTEXT = "fetch_context"
    UPDATE_STATE = "update_state"
    RESPONSE = "response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class MCPToolInvocationRequest(BaseModel):
    """Schema for tool invocation requests"""
    message_type: Literal[MCPMessageType.INVOKE_TOOL] = MCPMessageType.INVOKE_TOOL
    request_id: str = Field(..., description="Unique identifier for this request")
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str = Field(..., description="ID of the requesting agent")
    tool_name: str = Field(..., description="Name of the tool to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1=highest, 10=lowest)")
    timeout: Optional[int] = Field(default=30, description="Timeout in seconds")

class MCPToolInvocationResponse(BaseModel):
    """Schema for tool invocation responses"""
    message_type: Literal[MCPMessageType.RESPONSE] = MCPMessageType.RESPONSE
    request_id: str = Field(..., description="ID of the original request")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Whether the tool execution was successful")
    result: Optional[Any] = Field(default=None, description="Tool execution result")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MCPContextFetchRequest(BaseModel):
    """Schema for context fetch requests"""
    message_type: Literal[MCPMessageType.FETCH_CONTEXT] = MCPMessageType.FETCH_CONTEXT
    request_id: str = Field(..., description="Unique identifier for this request")
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str = Field(..., description="ID of the requesting agent")
    context_keys: List[str] = Field(..., description="List of context keys to fetch")
    scope: Literal["agent", "session", "global"] = Field(default="session", description="Context scope")

class MCPContextFetchResponse(BaseModel):
    """Schema for context fetch responses"""
    message_type: Literal[MCPMessageType.RESPONSE] = MCPMessageType.RESPONSE
    request_id: str = Field(..., description="ID of the original request")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Whether the context fetch was successful")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Retrieved context data")
    missing_keys: List[str] = Field(default_factory=list, description="Keys that were not found")

class MCPStateUpdateRequest(BaseModel):
    """Schema for state update requests"""
    message_type: Literal[MCPMessageType.UPDATE_STATE] = MCPMessageType.UPDATE_STATE
    request_id: str = Field(..., description="Unique identifier for this request")
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str = Field(..., description="ID of the requesting agent")
    state_updates: Dict[str, Any] = Field(..., description="State updates to apply")
    scope: Literal["agent", "session", "global"] = Field(default="session", description="Update scope")
    merge_strategy: Literal["replace", "merge", "append"] = Field(default="merge", description="How to apply updates")

class MCPStateUpdateResponse(BaseModel):
    """Schema for state update responses"""
    message_type: Literal[MCPMessageType.RESPONSE] = MCPMessageType.RESPONSE
    request_id: str = Field(..., description="ID of the original request")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(..., description="Whether the state update was successful")
    updated_keys: List[str] = Field(default_factory=list, description="Keys that were updated")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

class MCPErrorResponse(BaseModel):
    """Schema for error responses"""
    message_type: Literal[MCPMessageType.ERROR] = MCPMessageType.ERROR
    request_id: str = Field(..., description="ID of the original request")
    timestamp: datetime = Field(default_factory=datetime.now)
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")

class MCPHeartbeatMessage(BaseModel):
    """Schema for heartbeat messages"""
    message_type: Literal[MCPMessageType.HEARTBEAT] = MCPMessageType.HEARTBEAT
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str = Field(..., description="ID of the agent sending heartbeat")
    status: Literal["active", "idle", "busy"] = Field(..., description="Agent status")
    load_metrics: Optional[Dict[str, float]] = Field(default=None, description="Optional load metrics")

# Union type for all MCP messages
MCPMessage = Union[
    MCPToolInvocationRequest,
    MCPToolInvocationResponse,
    MCPContextFetchRequest,
    MCPContextFetchResponse,
    MCPStateUpdateRequest,
    MCPStateUpdateResponse,
    MCPErrorResponse,
    MCPHeartbeatMessage
]

class MCPConnectionConfig(BaseModel):
    """Configuration for MCP connections"""
    server_url: str = Field(..., description="MCP server URL")
    client_id: str = Field(..., description="Client identifier")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    timeout: int = Field(default=30, description="Default timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")

class MCPServerInfo(BaseModel):
    """Server information and capabilities"""
    server_id: str = Field(..., description="Server identifier")
    version: str = Field(default=MCP_VERSION, description="MCP version")
    schema_version: str = Field(default=SCHEMA_VERSION, description="Schema version")
    capabilities: List[str] = Field(..., description="List of supported capabilities")
    supported_tools: List[str] = Field(default_factory=list, description="List of available tools")
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests")

def validate_mcp_message(message_data: Dict[str, Any]) -> MCPMessage:
    """
    Validate and parse an MCP message from raw data.
    
    Args:
        message_data: Raw message data dictionary
        
    Returns:
        Parsed and validated MCP message
        
    Raises:
        ValueError: If message is invalid or unsupported type
    """
    message_type = message_data.get("message_type")
    
    if message_type == MCPMessageType.INVOKE_TOOL:
        return MCPToolInvocationRequest(**message_data)
    elif message_type == MCPMessageType.FETCH_CONTEXT:
        return MCPContextFetchRequest(**message_data)
    elif message_type == MCPMessageType.UPDATE_STATE:
        return MCPStateUpdateRequest(**message_data)
    elif message_type == MCPMessageType.RESPONSE:
        # Need to determine response type based on original request
        if "result" in message_data or "execution_time" in message_data:
            return MCPToolInvocationResponse(**message_data)
        elif "context_data" in message_data:
            return MCPContextFetchResponse(**message_data)
        elif "updated_keys" in message_data:
            return MCPStateUpdateResponse(**message_data)
        else:
            raise ValueError(f"Cannot determine response type for message: {message_data}")
    elif message_type == MCPMessageType.ERROR:
        return MCPErrorResponse(**message_data)
    elif message_type == MCPMessageType.HEARTBEAT:
        return MCPHeartbeatMessage(**message_data)
    else:
        raise ValueError(f"Unsupported message type: {message_type}")

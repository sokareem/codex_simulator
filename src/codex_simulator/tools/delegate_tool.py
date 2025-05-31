import asyncio
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Add MCP imports
from ..mcp import MCPClient, MCPToolInvocationRequest

class DelegateToolInput(BaseModel):
    """Input schema for the delegation tool."""
    task: str = Field(..., description="The task to delegate")
    context: str = Field("", description="Optional context information for the task")
    coworker: str = Field(..., description="The name/role of the coworker to delegate to")

class DelegateTool(BaseTool):
    """Tool for delegating tasks to other agents."""
    name: str = "delegate_tool"
    description: str = "Delegates a specific task to a specialist coworker (FileNavigator, CodeExecutor, WebResearcher)"
    args_schema: Type[BaseModel] = DelegateToolInput
    
    # Define agents_dict as a class attribute with annotation
    agents_dict: Dict[str, Any] = {}
    
    # Add model_config to allow arbitrary types (for storing agent references)
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, agents_dict=None):
        super().__init__()
        # Now we can safely set agents_dict
        if agents_dict:
            self.agents_dict = agents_dict
    
    def _extract_str_from_dict(self, value: Any) -> str:
        """Extract string value from a dictionary or return as is."""
        if isinstance(value, dict):
            # Try common field names
            for field in ["description", "content", "text", "value"]:
                if field in value:
                    return str(value[field])
            # Fall back to string representation
            return str(value)
        return str(value) if value is not None else ""
    
    def _run(self, task: str, coworker: str, context: str = "") -> str:
        """
        Delegate a task to another agent and return the result.
        
        Args:
            task: The task to delegate (simple string description)
            context: Additional context for the task (simple string)
            coworker: The agent to delegate to (e.g., 'FileNavigator', 'CodeExecutor')
        
        Returns:
            The result from the delegated agent
        """
        # Debug info to help troubleshoot
        print(f"Delegation attempt - Task: {task[:50]}..., Coworker: {coworker}")
        print(f"Available agents: {list(self.agents_dict.keys())}")
        
        # Handle complex objects by extracting string values
        if not isinstance(task, str):
            task = self._extract_str_from_dict(task)
        if not isinstance(context, str):
            context = self._extract_str_from_dict(context)
        if not isinstance(coworker, str):
            coworker = self._extract_str_from_dict(coworker)
        
        # Find the target agent with more flexible matching
        target_agent = None
        target_name = None
        
        # Try exact match first
        if coworker in self.agents_dict:
            target_agent = self.agents_dict[coworker]
            target_name = coworker
        else:
            # Try case-insensitive partial matches
            coworker_lower = coworker.lower()
            for name, agent in self.agents_dict.items():
                if (coworker_lower in name.lower() or 
                    name.lower() in coworker_lower or
                    name.lower().replace(" ", "") in coworker_lower or
                    coworker_lower.replace(" ", "") in name.lower()):
                    target_agent = agent
                    target_name = name
                    print(f"Found agent match: '{name}'")
                    break
        
        if not target_agent:
            return f"Error: Could not find agent '{coworker}' for delegation. Available agents: {', '.join(self.agents_dict.keys())}"
        
        # Prepare the task with context
        full_task = task
        if context:
            full_task = f"{task}\n\nContext: {context}"
            
        # Execute the task on the target agent
        print(f"Delegating to '{target_name}' with task: {task[:50]}...")
        try:
            if hasattr(target_agent, 'execute'):
                return target_agent.execute(full_task)
            elif hasattr(target_agent, 'run'):
                return target_agent.run(full_task)
            else:
                return f"Error: Agent has no executable method. Available methods: {[m for m in dir(target_agent) if not m.startswith('_') and callable(getattr(target_agent, m))]}"
        except Exception as e:
            return f"Error delegating task: {str(e)}"

class MCPDelegateTool(BaseTool):
    """MCP-enabled delegation tool for agent communication"""
    name: str = "mcp_delegate_tool"
    description: str = "Delegates tasks to specialist agents via MCP protocol"
    args_schema: Type[BaseModel] = DelegateToolInput
    
    agents_dict: Dict[str, Any] = {}
    mcp_client: Optional[MCPClient] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, agents_dict=None, mcp_client=None):
        super().__init__()
        if agents_dict:
            self.agents_dict = agents_dict
        self.mcp_client = mcp_client
    
    def _extract_str_from_dict(self, value: Any) -> str:
        """Extract string value from a dictionary or return as is."""
        if isinstance(value, dict):
            # Try common field names
            for field in ["description", "content", "text", "value"]:
                if field in value:
                    return str(value[field])
            # Fall back to string representation
            return str(value)
        return str(value) if value is not None else ""
    
    async def _delegate_via_mcp(self, task: str, coworker: str, context: str = "") -> str:
        """Delegate task via MCP client"""
        if not self.mcp_client:
            return "MCP client not available for delegation"
        
        try:
            # Prepare delegation request
            agent_mapping = {
                "filenavigator": "file_navigator_agent",
                "codeexecutor": "code_executor_agent", 
                "webresearcher": "web_researcher_agent"
            }
            
            agent_tool = agent_mapping.get(coworker.lower().replace(" ", ""))
            if not agent_tool:
                return f"Unknown coworker: {coworker}. Available: FileNavigator, CodeExecutor, WebResearcher"
            
            # Create full task description
            full_task = f"{task}\n\nContext: {context}" if context else task
            
            # Invoke via MCP
            response = await self.mcp_client.invoke_tool(
                tool_name=agent_tool,
                arguments={"task": full_task},
                timeout=60
            )
            
            if response.success:
                return f"{coworker} completed the task: {response.result}"
            else:
                return f"Error delegating to {coworker}: {response.error_message}"
                
        except Exception as e:
            return f"MCP delegation failed: {str(e)}"
    
    def _run(self, task: str, coworker: str, context: str = "") -> str:
        """Execute delegation with MCP support"""
        # Extract string values if inputs are dicts
        task = self._extract_str_from_dict(task)
        coworker = self._extract_str_from_dict(coworker)
        context = self._extract_str_from_dict(context)
        
        # Check if MCP client is available
        if self.mcp_client:
            # Run async delegation
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task for async execution
                task_coro = self._delegate_via_mcp(task, coworker, context)
                future = asyncio.ensure_future(task_coro)
                try:
                    return loop.run_until_complete(future)
                except Exception as e:
                    return f"Async delegation failed: {str(e)}"
            else:
                return loop.run_until_complete(self._delegate_via_mcp(task, coworker, context))
        
        # Fallback to direct delegation if MCP not available
        return self._direct_delegate(task, coworker, context)
    
    def _direct_delegate(self, task: str, coworker: str, context: str = "") -> str:
        """Direct delegation fallback method"""
        # Find matching agent
        for agent_name, agent in self.agents_dict.items():
            if coworker.lower().replace(" ", "") == agent_name.lower().replace(" ", ""):
                try:
                    # Create full task description
                    full_task = f"{task}\n\nContext: {context}" if context else task
                    
                    # Try different execution methods
                    if hasattr(agent, 'execute'):
                        result = agent.execute(full_task)
                    elif hasattr(agent, 'run'):
                        result = agent.run(full_task)
                    else:
                        return f"Agent {coworker} does not have an executable method"
                    
                    return str(result)
                    
                except Exception as e:
                    return f"Error executing task with {coworker}: {str(e)}"
        
        # If no exact match, try partial matching
        for agent_name, agent in self.agents_dict.items():
            if coworker.lower() in agent_name.lower() or agent_name.lower() in coworker.lower():
                try:
                    full_task = f"{task}\n\nContext: {context}" if context else task
                    
                    if hasattr(agent, 'execute'):
                        result = agent.execute(full_task)
                    elif hasattr(agent, 'run'):
                        result = agent.run(full_task)
                    else:
                        return f"Agent {agent_name} does not have an executable method"
                    
                    return str(result)
                    
                except Exception as e:
                    return f"Error executing task with {agent_name}: {str(e)}"
        
        available_agents = ", ".join(self.agents_dict.keys())
        return f"Could not find agent '{coworker}'. Available agents: {available_agents}"

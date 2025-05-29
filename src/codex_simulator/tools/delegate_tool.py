from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

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

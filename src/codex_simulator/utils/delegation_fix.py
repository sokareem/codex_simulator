"""
Utility functions for handling delegation between agents in CrewAI.
This provides alternative ways to handle delegation without monkey patching.
"""
import json
from typing import Optional, Dict, Any

def normalize_delegation_input(input_data: Any) -> str:
    """
    Normalize input data to string format, handling JSON and dictionary inputs.
    
    Args:
        input_data: Input data that could be string, dict, or JSON string
        
    Returns:
        Normalized string representation
    """
    # Handle dictionary input
    if isinstance(input_data, dict):
        # Try multiple common dictionary structures
        if "description" in input_data:
            return str(input_data.get("description", ""))
        elif "content" in input_data:
            return str(input_data.get("content", ""))  
        elif "text" in input_data:
            return str(input_data.get("text", ""))
        elif "value" in input_data:
            return str(input_data.get("value", ""))
        else:
            # Convert dict to a reasonable string representation
            return str(input_data)
    
    # Handle JSON string input
    if isinstance(input_data, str) and input_data.startswith("{"):
        try:
            data_dict = json.loads(input_data)
            if isinstance(data_dict, dict):
                # Try multiple common dictionary structures
                if "description" in data_dict:
                    return str(data_dict.get("description", ""))
                elif "content" in data_dict:
                    return str(data_dict.get("content", ""))
                elif "text" in data_dict:
                    return str(data_dict.get("text", ""))
                elif "value" in data_dict:
                    return str(data_dict.get("value", ""))
        except:
            pass  # If JSON parsing fails, return the original string
    
    # Return as-is if it's already a string or other type
    return str(input_data)

def get_delegation_handler(agents_dict):
    """
    Create a delegation handler that can be used to delegate tasks between agents.
    
    Args:
        agents_dict: Dictionary mapping agent names/roles to agent instances
        
    Returns:
        Function that handles delegation
    """
    def delegate_task(task: Any, context: Optional[Any] = None, to: Optional[Any] = None):
        """
        Delegate a task to another agent.
        
        Args:
            task: Task description
            context: Context information
            to: Target agent name or identifier
            
        Returns:
            Result from the agent
        """
        # New format for delegation inputs - simpler flat strings
        task_str = task if isinstance(task, str) else normalize_delegation_input(task)
        context_str = context if isinstance(context, str) else normalize_delegation_input(context) if context else ""
        to_str = to if isinstance(to, str) else normalize_delegation_input(to) if to else ""
        
        # Debug information to help with troubleshooting
        print(f"Delegating to: '{to_str}'")
        print(f"Available agents: {list(agents_dict.keys())}")
        
        # Find the target agent
        target_agent = None
        if to_str in agents_dict:
            target_agent = agents_dict[to_str]
        else:
            # Try case-insensitive comparison
            for key, agent in agents_dict.items():
                if to_str.lower() == key.lower() or to_str.lower() in key.lower() or key.lower() in to_str.lower():
                    target_agent = agent
                    print(f"Found match using fuzzy comparison: '{key}'")
                    break
        
        if not target_agent:
            return f"Error: Could not find agent '{to_str}' for delegation. Available agents: {', '.join(agents_dict.keys())}"
        
        # Create a task description combining task and context
        full_task = task_str
        if context_str:
            full_task = f"{task_str}\n\nContext: {context_str}"
            
        # Run the target agent
        try:
            # Use agent's simple input mechanism - different for each crewai version
            if hasattr(target_agent, 'execute'):
                print(f"Using execute() method on agent")
                return target_agent.execute(full_task)
            elif hasattr(target_agent, 'run'):
                print(f"Using run() method on agent") 
                return target_agent.run(full_task)
            else:
                available_methods = [method for method in dir(target_agent) if not method.startswith('_')]
                print(f"Available methods: {available_methods}")
                return f"Error: Agent doesn't have a known execution method"
        except Exception as e:
            return f"Error delegating task: {str(e)}"
    
    return delegate_task

def apply_delegation_fix():
    """
    Placeholder function to maintain compatibility with existing code.
    Previously fixed delegation issues by monkey patching, but now we use our custom delegate tool.
    """
    print("Using custom delegation tool mechanism instead of monkey patching")
    pass

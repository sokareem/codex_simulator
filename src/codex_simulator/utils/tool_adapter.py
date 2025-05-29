"""
Tool adapter utilities to fix incompatibilities between different CrewAI versions
"""
from typing import Dict, Any, Optional, Union, Callable

def create_simple_tool_adapter(tool_func: Callable):
    """
    Create an adapter for tools that handles various input formats.
    This fixes "unhashable type: 'dict'" errors when tools are called with dictionary inputs.
    
    Args:
        tool_func: The original tool function
        
    Returns:
        Wrapped tool function that handles different input formats
    """
    def adapter_func(*args, **kwargs):
        # If we have a single dictionary argument, extract key values
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            # Extract values from dict and call the function with them
            dict_input = args[0]
            # Convert to kwargs based on expected parameter names
            return tool_func(**dict_input)
        
        # Handle JSON string case
        if len(args) == 1 and isinstance(args[0], str) and args[0].startswith('{'):
            import json
            try:
                dict_input = json.loads(args[0])
                if isinstance(dict_input, dict):
                    return tool_func(**dict_input)
            except:
                pass  # Fall through to standard handling if JSON parsing fails
        
        # Otherwise call normally
        return tool_func(*args, **kwargs)
    
    return adapter_func

def patch_tool_methods(agent):
    """
    Patch all tool methods of an agent to handle different input formats.
    
    Args:
        agent: The agent to patch
    """
    if not hasattr(agent, 'tools'):
        return
        
    for tool in agent.tools:
        if hasattr(tool, '_run'):
            tool._original_run = tool._run  # Save original method
            tool._run = create_simple_tool_adapter(tool._run)  # Replace with adapted version

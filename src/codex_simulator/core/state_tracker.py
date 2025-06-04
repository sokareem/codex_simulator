import os
import re
from typing import Optional, List, Any
from dataclasses import dataclass

@dataclass
class ExecutionState:
    """Track execution state for safe termination"""
    is_running: bool = False
    stop_requested: bool = False
    current_task: Optional[str] = None
    execution_thread: Optional[Any] = None

class StateTracker:
    """Tracks state across agent interactions"""
    def __init__(self, initial_cwd: str = os.getcwd()):
        self.cwd = initial_cwd
        self.command_history = []
        self.context_data = {}
    
    def update_cwd(self, new_cwd: str) -> bool:
        """Update current working directory if it exists"""
        if os.path.isdir(new_cwd):
            self.cwd = os.path.abspath(new_cwd)
            return True
        return False
    
    def add_command(self, command: str) -> None:
        """Add a command to the history"""
        self.command_history.append(command)
    
    def update_context(self, key: str, value: Any) -> None:
        """Update a context value"""
        self.context_data[key] = value
    
    def extract_cwd_from_response(self, response: str) -> Optional[str]:
        """Extract updated CWD from a response if present"""
        patterns = [
            r"Changed directory to: ([^\n]+)",
            r"Current working directory: ([^\n]+)",
            r"CWD: ([^\n]+)",
            r"Current directory: ([^\n]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                potential_cwd = match.group(1).strip()
                if os.path.isdir(potential_cwd):
                    return potential_cwd
        
        return None

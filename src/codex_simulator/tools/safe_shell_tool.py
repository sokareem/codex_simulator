import os
import re
import subprocess
from typing import Dict, List, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeShellToolInput(BaseModel):
    """Input for the SafeShellTool."""
    command: str = Field(..., description="The shell command to execute.")

class SafeShellTool(BaseTool):
    """A tool to safely execute shell commands with strict safety checks."""
    name: str = "safe_shell_tool"
    description: str = "Safely executes shell commands with security restrictions."
    args_schema: Type[BaseModel] = SafeShellToolInput
    
    # Commands that are explicitly allowed
    allowed_commands: List[str] = ["ls", "pwd", "cat", "echo", "find", "grep", "python", "pip"]
    
    # Commands and patterns that are explicitly blocked
    blocked_commands: List[str] = ["rm", "sudo", "su", "chmod", "chown", "mkfs", "dd", "mv"]
    blocked_patterns: List[str] = [">", "|", ";", "&&", "||", "`", "$", "eval", "exec"]

    def __init__(self, 
                 allowed_commands: List[str] = None, 
                 blocked_commands: List[str] = None,
                 blocked_patterns: List[str] = None):
        super().__init__()
        if allowed_commands:
            self.allowed_commands = allowed_commands
        if blocked_commands:
            self.blocked_commands = blocked_commands
        if blocked_patterns:
            self.blocked_patterns = blocked_patterns

    def _is_safe_command(self, command: str) -> Dict[str, bool]:
        """Check if a command is safe to execute."""
        command_parts = command.split()
        if not command_parts:
            return {"safe": False, "reason": "Empty command"}
        
        base_command = command_parts[0]
        
        # Check if command is in allowed list
        if base_command not in self.allowed_commands:
            return {"safe": False, "reason": f"Command '{base_command}' is not in the allowed list"}
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in command_parts:
                return {"safe": False, "reason": f"Command contains blocked term: '{blocked}'"}
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command:
                return {"safe": False, "reason": f"Command contains blocked pattern: '{pattern}'"}
        
        return {"safe": True, "reason": "Command passed safety checks"}

    def _run(self, command: str) -> str:
        """Run the shell command if it passes safety checks."""
        safety_check = self._is_safe_command(command)
        
        if not safety_check["safe"]:
            return f"Error: Cannot execute command. {safety_check['reason']}"
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                return f"Command executed with errors. Exit code: {result.returncode}\n{result.stderr}"
            
            return result.stdout
        
        except subprocess.TimeoutExpired:
            return "Error: Command execution timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

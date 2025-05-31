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
    allowed_commands: List[str] = [
        "ls", "pwd", "cat", "echo", "find", "grep", "python", "pip",
        "df", "du", "ps", "top", "uname", "whoami", "history", "which",
        "tar", "zip", "unzip"
    ]
    
    # Commands and patterns that are explicitly blocked
    blocked_commands: List[str] = ["rm", "sudo", "su", "chmod", "chown", "mkfs", "dd", "mv"]
    blocked_patterns: List[str] = [">", "|", ";", "&&", "||", "`", "$", "eval", "exec"]

    def __init__(self, 
                 allowed_commands: List[str] = None, 
                 blocked_commands: List[str] = None,
                 blocked_patterns: List[str] = None,
                 **kwargs):
        """Initialize the SafeShellTool with optional custom settings."""
        super().__init__(**kwargs)
        
        # Use provided lists or defaults
        if allowed_commands is not None:
            self.allowed_commands = allowed_commands
        if blocked_commands is not None:
            self.blocked_commands = blocked_commands
        if blocked_patterns is not None:
            self.blocked_patterns = blocked_patterns

    def _is_command_safe(self, command: str) -> tuple[bool, str]:
        """Check if a command is safe to execute."""
        if not command.strip():
            return False, "Empty command."
        
        # Extract the base command (first word)
        base_command = command.strip().split()[0]
        
        # Check against blocked commands
        if base_command in self.blocked_commands:
            return False, f"Command '{base_command}' is blocked for security reasons."
        
        # Check against blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command:
                return False, f"Command contains blocked pattern '{pattern}' for security reasons."
        
        # Check against allowed commands
        if base_command not in self.allowed_commands:
            return False, f"Command '{base_command}' is not allowed for security reasons."
        
        return True, "Command is safe"

    def _handle_python_execution(self, command: str) -> str:
        """Handle Python script execution with file creation if needed."""
        # Check for Python code blocks in the command
        if "```python" in command and "```" in command:
            # Extract the Python script filename and code
            parts = command.split("```python")
            if len(parts) > 1:
                script_part = parts[1].split("```")[0]
                # Extract filename from the original command
                cmd_parts = command.split()
                if len(cmd_parts) > 1 and cmd_parts[1].endswith(".py"):
                    script_filename = cmd_parts[1]
                    
                    # Create the script file if it doesn't exist
                    if not os.path.exists(script_filename):
                        try:
                            with open(script_filename, 'w') as f:
                                f.write(script_part.strip())
                        except Exception as e:
                            return f"Error creating script file: {str(e)}"
        
        return None  # Continue with normal execution

    def _run(self, command: str) -> str:
        """Execute the shell command safely."""
        # Safety check
        is_safe, message = self._is_command_safe(command)
        if not is_safe:
            return f"Error: {message}"
        
        # Handle special Python execution
        python_result = self._handle_python_execution(command)
        if python_result:
            return python_result
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Handle permission denied for Python scripts
            if result.returncode != 0 and "Permission denied" in result.stderr and command.startswith("python"):
                # Try to fix permissions and retry
                cmd_parts = command.split()
                if len(cmd_parts) > 1 and cmd_parts[1].endswith(".py"):
                    script_file = cmd_parts[1]
                    if os.path.exists(script_file):
                        try:
                            current_mode = os.stat(script_file).st_mode
                            os.chmod(script_file, current_mode | 0o100)
                            # Retry execution
                            result = subprocess.run(
                                command,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                        except Exception as e:
                            return f"Error fixing permissions: {str(e)}"
            
            # Return the result
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully (no output)"
            else:
                return f"Command failed with return code {result.returncode}:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Error: Command '{command}' timed out after 60 seconds."
        except Exception as e:
            return f"Error executing command '{command}': {str(e)}"

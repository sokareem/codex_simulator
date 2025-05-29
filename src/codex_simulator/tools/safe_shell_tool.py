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
        """Execute a shell command if it passes safety checks."""
        # Check if this is a python script execution command
        executing_python_file = False
        python_command = None
        if command.startswith(('python ', 'python3 ')):
            parts = command.split(maxsplit=1)
            if len(parts) > 1 and parts[1].endswith('.py'):
                executing_python_file = True
                python_command = parts[0]  # 'python' or 'python3'
        
        # Check if it's a valid command
        command_parts = command.split()
        if not command_parts:
            return "Error: Empty command."
        
        base_command = command_parts[0]
        
        # Check against allowed commands
        if base_command not in self.allowed_commands:
            return f"Error: Command '{base_command}' is not allowed for security reasons. Allowed commands: {', '.join(self.allowed_commands)}"
        
        # Check against blocked commands
        if base_command in self.blocked_commands:
            return f"Error: Command '{base_command}' is blocked for security reasons."
        
        # Check against blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command:
                return f"Error: Command contains blocked pattern '{pattern}' for security reasons."
        
        try:
            # For Python file execution, handle file creation/writing if needed
            if executing_python_file:
                file_path = command_parts[1]
                
                # If the file doesn't exist and it's in the command, we might need to create it
                if not os.path.exists(file_path) and "def" in command and "print" in command:
                    # Extract potential Python code from the command if it looks like a code block
                    potential_code = None
                    if "```python" in command:
                        # Try to extract code from a markdown-style code block
                        code_parts = command.split("```python")
                        if len(code_parts) > 1:
                            code_end = code_parts[1].split("```")
                            if len(code_end) > 0:
                                potential_code = code_end[0].strip()
                    
                    if potential_code:
                        # Create the file with the extracted code
                        try:
                            with open(file_path, 'w') as f:
                                f.write(potential_code)
                            print(f"Created Python file: {file_path}")
                        except Exception as e:
                            return f"Error creating Python file {file_path}: {str(e)}"
            
            # Execute the command
            print(f"Executing command: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            
            # Format the output
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n\n"
                output += "Error: " + result.stderr
                    
            if not output:
                output = f"Command '{command}' executed successfully (no output)"
                
            # Include the executable permission info if we're trying to run a Python script
            if executing_python_file and "Permission denied" in output:
                # Try to make it executable and run again
                file_path = command_parts[1]
                try:
                    # Add execute permission
                    os.chmod(file_path, os.stat(file_path).st_mode | 0o100)
                    print(f"Added execute permission to: {file_path}")
                    
                    # Run again
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                    
                    # Update output
                    output = ""
                    if result.stdout:
                        output += result.stdout
                    if result.stderr:
                        if output:
                            output += "\n\n"
                        output += "Error: " + result.stderr
                        
                    if not output:
                        output = f"Command '{command}' executed successfully after adding execute permission (no output)"
                except Exception as e:
                    output += f"\n\nTried to add execute permission but failed: {str(e)}"
                    output += f"\n\nAlternative: Try running with 'python {file_path}' instead of './{file_path}'"
            
            return output
        except subprocess.TimeoutExpired:
            return f"Error: Command '{command}' timed out after 60 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

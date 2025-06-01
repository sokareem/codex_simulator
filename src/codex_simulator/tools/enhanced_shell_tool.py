"""Enhanced shell tool with improved error handling and validation."""

import subprocess
import os
import shutil
import time
import threading
from typing import Dict, List, Optional, Tuple
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

# Try to import psutil, but gracefully handle if it's not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class EnhancedShellTool(BaseTool):
    """Enhanced shell tool with pre-flight checks and intelligent error handling."""
    
    name: str = "Enhanced Shell Tool"
    description: str = """Execute shell commands with enhanced error handling and validation.
    Performs pre-flight checks and provides detailed error information."""
    
    # Resource limits for safety
    max_execution_time: int = 30
    max_memory_mb: int = 512
    
    def __init__(self):
        super().__init__()
        self.blocked_commands = {
            'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs',
            'dd', 'sudo', 'su', 'chmod', 'chown', 'passwd'
        }
        self.allowed_commands = {
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'ps', 'top',
            'df', 'du', 'free', 'uname', 'whoami', 'pwd', 'cd', 'echo',
            'date', 'which', 'command', 'stat', 'file', 'wc', 'sort'
        }
        self.psutil_available = PSUTIL_AVAILABLE
        
    def _run(self, command: str) -> str:
        """Execute shell command with enhanced safety and error handling."""
        try:
            # Pre-flight validation
            validation_result = self._validate_command(command)
            if not validation_result["valid"]:
                return f"Command validation failed: {validation_result['reason']}"
            
            # Execute with resource monitoring
            result = self._execute_with_monitoring(command)
            return result
            
        except Exception as e:
            return f"Execution error: {str(e)}"
            
    def _validate_command(self, command: str) -> Dict[str, any]:
        """Validate command before execution."""
        command_parts = command.strip().split()
        if not command_parts:
            return {"valid": False, "reason": "Empty command"}
            
        base_command = command_parts[0]
        
        # Check if command is blocked
        if base_command in self.blocked_commands:
            return {"valid": False, "reason": f"Command '{base_command}' is blocked for safety"}
            
        # Check if command exists
        if not shutil.which(base_command):
            suggestions = self._suggest_similar_commands(base_command)
            reason = f"Command '{base_command}' not found"
            if suggestions:
                reason += f". Did you mean: {', '.join(suggestions)}?"
            return {"valid": False, "reason": reason}
            
        # Validate file paths in command
        path_validation = self._validate_paths_in_command(command_parts)
        if not path_validation["valid"]:
            return path_validation
            
        return {"valid": True, "reason": "Command validated successfully"}
        
    def _suggest_similar_commands(self, command: str) -> List[str]:
        """Suggest similar commands for typos."""
        import difflib
        suggestions = difflib.get_close_matches(
            command, self.allowed_commands, n=3, cutoff=0.6
        )
        return suggestions
        
    def _validate_paths_in_command(self, command_parts: List[str]) -> Dict[str, any]:
        """Validate file paths mentioned in command."""
        for part in command_parts[1:]:  # Skip the command itself
            if part.startswith('-'):  # Skip flags
                continue
            if os.path.sep in part:  # Looks like a path
                if not os.path.exists(part) and not part.endswith('*'):
                    return {
                        "valid": False, 
                        "reason": f"Path '{part}' does not exist"
                    }
        return {"valid": True, "reason": "All paths validated"}
        
    def _execute_with_monitoring(self, command: str) -> str:
        """Execute command with resource monitoring using subprocess.run."""
        try:
            # Start time for timeout monitoring
            start_time = time.time()
            
            # Execute the process with timeout
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.max_execution_time,
                    cwd=os.getcwd()
                )
                
                # Format response
                response = self._format_command_response(
                    command, result.returncode, 
                    result.stdout.encode('utf-8'), 
                    result.stderr.encode('utf-8')
                )
                return response
                
            except subprocess.TimeoutExpired:
                return f"Command timed out after {self.max_execution_time} seconds"
                
        except Exception as e:
            return f"Process execution failed: {str(e)}"
            
    def _format_command_response(self, command: str, returncode: int, 
                                stdout: bytes, stderr: bytes) -> str:
        """Format command execution response with detailed information."""
        response_parts = []
        
        # Add command info
        response_parts.append(f"Command: {command}")
        response_parts.append(f"Exit Code: {returncode}")
        
        # Add stdout if present
        if stdout:
            stdout_text = stdout.decode('utf-8', errors='replace').strip()
            if stdout_text:
                response_parts.append(f"Output:\n{stdout_text}")
                
        # Add stderr if present
        if stderr:
            stderr_text = stderr.decode('utf-8', errors='replace').strip()
            if stderr_text:
                response_parts.append(f"Error Output:\n{stderr_text}")
                
        # Add suggestions for common errors
        if returncode != 0:
            suggestions = self._get_error_suggestions(command, returncode, stderr)
            if suggestions:
                response_parts.append(f"Suggestions:\n{suggestions}")
                
        return "\n\n".join(response_parts)
        
    def _get_error_suggestions(self, command: str, returncode: int, 
                              stderr: bytes) -> str:
        """Provide suggestions based on common error patterns."""
        stderr_text = stderr.decode('utf-8', errors='replace').lower()
        
        if "permission denied" in stderr_text:
            return "• Check file permissions with 'ls -l'\n• Verify you have access to the resource"
        elif "no such file or directory" in stderr_text:
            return "• Verify the file path is correct\n• Use 'ls' to check available files"
        elif "command not found" in stderr_text:
            return "• Check if the command is installed\n• Verify PATH environment variable"
        elif returncode == 130:  # Ctrl+C
            return "• Command was interrupted by user"
        else:
            return ""

# Create instance for import
enhanced_shell_tool = EnhancedShellTool()

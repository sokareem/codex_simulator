import os
from typing import Type, Dict, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from codex_simulator.utils.permission_manager import PermissionManager

class SafeFileWriteToolInput(BaseModel):
    """Input for the SafeFileWriteTool."""
    file_path: str = Field(..., description="Path to the file to write to")
    content: str = Field(..., description="Content to write to the file")
    append: bool = Field(False, description="Whether to append to the file or overwrite it")

class SafeFileWriteTool(BaseTool):
    """A tool to safely write to files with user permission."""
    name: str = "safe_file_write_tool"
    description: str = "Writes content to files after obtaining user permission. Requires approval before writing."
    args_schema: Type[BaseModel] = SafeFileWriteToolInput
    
    # Define permission_manager as a class field to avoid Pydantic errors
    permission_manager: Optional[PermissionManager] = None
    
    # Only critically dangerous files should be blocked
    blocked_files: List[str] = [
        ".bashrc", ".zshrc", ".bash_profile", ".ssh/config", 
        "authorized_keys", "known_hosts", "id_rsa", "id_rsa.pub"
    ]
    
    # Don't allow writing to system-critical paths
    blocked_paths: List[str] = [
        "/etc", "/var", "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/lib", "/root", 
        "/boot", "/dev", "/proc", "/sys", "/tmp"
    ]
    
    def __init__(self, allowed_files: List[str] = None):
        """Initialize the tool with allowed files and create a permission manager."""
        super().__init__()
        if allowed_files:
            self.blocked_files = [f for f in self.blocked_files if f not in allowed_files]
        self.permission_manager = PermissionManager()

    def _is_safe_path(self, file_path: str) -> Dict[str, bool]:
        """Check if a file path is safe to write to."""
        # Normalize the path
        file_path = os.path.abspath(os.path.expanduser(file_path))
        
        # Check the filename for critical system files
        filename = os.path.basename(file_path)
        if filename in self.blocked_files:
            return {
                "safe": False, 
                "reason": f"File '{filename}' is restricted for security reasons."
            }
        
        # Check for blocked system paths
        for blocked in self.blocked_paths:
            blocked = os.path.abspath(os.path.expanduser(blocked))
            if file_path.startswith(blocked):
                return {"safe": False, "reason": f"Path contains blocked directory: '{blocked}'"}
        
        return {"safe": True, "reason": ""}

    def _run(self, file_path: str, content: str, append: bool = False) -> str:
        """Write to the file if it passes safety checks and user approves."""
        # Check if the path is safe
        safety_check = self._is_safe_path(file_path)
        if not safety_check["safe"]:
            return f"Error: {safety_check['reason']}"
        
        try:
            file_path = os.path.abspath(os.path.expanduser(file_path))
            operation = "append to" if append else "write to"
            
            # Request permission from the user
            if not self.permission_manager.request_file_write_permission(
                file_path, content, operation
            ):
                return f"Operation cancelled: {operation} {file_path}"
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # Write the file after permission is granted
            mode = "a" if append else "w"
            with open(file_path, mode, encoding="utf-8") as file:
                file.write(content)
            
            return f"Successfully {operation} {file_path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"

import os
from typing import List, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeFileReadToolInput(BaseModel):
    """Input for the SafeFileReadTool."""
    file_path: str = Field(..., description="The path of the file to read.")

class SafeFileReadTool(BaseTool):
    """A tool to safely read file contents with security checks."""
    name: str = "safe_file_read_tool"
    description: str = "Safely reads the contents of a file with security restrictions."
    args_schema: Type[BaseModel] = SafeFileReadToolInput
    
    # Sensitive files and directories that should not be accessed
    blocked_paths: List[str] = [
        ".env", "id_rsa", ".ssh/", "/etc/passwd", "/etc/shadow",
        "C:\\Windows\\", "C:\\Program Files\\", "C:\\Users\\Administrator\\"
    ]
    
    # Maximum file size to read (1MB)
    max_file_size: int = 1024 * 1024

    def _is_safe_file(self, file_path: str) -> bool:
        """Check if a file is safe to access."""
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        
        # Check against blocked paths
        for blocked in self.blocked_paths:
            if blocked in abs_path:
                return False
        
        # Check file size
        try:
            if os.path.exists(abs_path) and os.path.getsize(abs_path) > self.max_file_size:
                return False
        except:
            pass
                
        return True

    def _run(self, file_path: str) -> str:
        """Read the contents of a file if it passes safety checks."""
        if not self._is_safe_file(file_path):
            return f"Error: Access to file '{file_path}' is restricted (file may be sensitive, too large, or blocked for security reasons)."
        
        try:
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' does not exist."
                
            if not os.path.isfile(file_path):
                return f"Error: Path '{file_path}' is not a file."
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return f"Contents of file '{file_path}':\n\n{content}"
            
        except PermissionError:
            return f"Error: Permission denied to access file '{file_path}'."
        except Exception as e:
            return f"Error reading file: {str(e)}"

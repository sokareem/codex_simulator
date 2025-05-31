import os
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeFileReadToolInput(BaseModel):
    """Input for the SafeFileReadTool."""
    file_path: str = Field(..., description="The path of the file to read.")

class SafeFileReadTool(BaseTool):
    """A tool to safely read file contents with minimal restrictions."""
    name: str = "safe_file_read_tool"
    description: str = "Reads the contents of almost any file, with exceptions for system and security-critical files."
    args_schema: Type[BaseModel] = SafeFileReadToolInput
    
    # Only critically sensitive files should be blocked
    blocked_files: List[str] = [
        "id_rsa", ".ssh/id_rsa", ".env", "credentials.json", "secrets.json",
        "authorized_keys"
    ]
    
    # Maximum file size to read (5MB)
    max_file_size: int = 5 * 1024 * 1024

    def _is_safe_file(self, file_path: str) -> dict:
        """Check if a file is safe to access."""
        # Convert to absolute path
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        
        # Check against blocked files
        for blocked in self.blocked_files:
            if blocked in abs_path:
                return {"safe": False, "reason": f"Access to '{blocked}' files is restricted for security reasons"}
        
        # Check if the file exists 
        if not os.path.exists(abs_path):
            return {"safe": False, "reason": f"File '{abs_path}' does not exist"}
            
        # Check if it's a directory
        if os.path.isdir(abs_path):
            return {"safe": False, "reason": f"Path '{abs_path}' is a directory, not a file. Use the directory tool instead."}
        
        # Check file size
        try:
            if os.path.getsize(abs_path) > self.max_file_size:
                return {"safe": False, "reason": f"File '{abs_path}' exceeds the maximum allowed size of {self.max_file_size/1024/1024:.1f}MB"}
        except Exception as e:
            return {"safe": False, "reason": f"Error checking file size: {str(e)}"}
                
        return {"safe": True, "reason": ""}

    def _run(self, file_path: str) -> str:
        """Read the contents of a file if it passes safety checks."""
        safety_check = self._is_safe_file(file_path)
        if not safety_check["safe"]:
            return f"Error: {safety_check['reason']}"
        
        try:
            abs_path = os.path.abspath(os.path.expanduser(file_path))
            
            # Try to detect binary files
            is_binary = False
            try:
                with open(abs_path, 'rb') as f:
                    initial_bytes = f.read(1024)
                    is_binary = b'\x00' in initial_bytes
            except:
                pass
                
            # Read and return file contents
            if is_binary:
                return f"File '{file_path}' appears to be binary. Cannot display content."
                
            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return f"Contents of file '{file_path}':\n\n{content}"
            
        except PermissionError:
            return f"Error: Permission denied to access file '{file_path}'."
        except Exception as e:
            return f"Error reading file: {str(e)}"

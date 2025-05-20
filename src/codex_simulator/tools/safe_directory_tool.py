import os
import re
from typing import List, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeDirectoryToolInput(BaseModel):
    """Input for the SafeDirectoryTool."""
    directory_path: str = Field(..., description="The path of the directory to read.")

class SafeDirectoryTool(BaseTool):
    """A tool to safely read directory contents with security checks."""
    name: str = "safe_directory_tool"
    description: str = "Safely reads the contents of a directory, listing files and subdirectories."
    args_schema: Type[BaseModel] = SafeDirectoryToolInput
    
    # Sensitive directories that should not be accessed
    blocked_directories: List[str] = [
        "/etc", "/var", "/root", "/dev", "/sys", "/proc", 
        "C:\\Windows", "C:\\Program Files", "C:\\Users\\Administrator"
    ]

    def _is_safe_path(self, path: str) -> bool:
        """Check if a path is safe to access."""
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Check against blocked directories
        for blocked in self.blocked_directories:
            if abs_path.startswith(blocked):
                return False
                
        return True

    def _run(self, directory_path: str) -> str:
        """List the contents of a directory if it passes safety checks."""
        if not self._is_safe_path(directory_path):
            return f"Error: Access to directory '{directory_path}' is restricted for security reasons."
        
        try:
            if not os.path.exists(directory_path):
                return f"Error: Directory '{directory_path}' does not exist."
                
            if not os.path.isdir(directory_path):
                return f"Error: Path '{directory_path}' is not a directory."
            
            items = os.listdir(directory_path)
            
            # Categorize items as files or directories
            files = []
            directories = []
            
            for item in items:
                full_path = os.path.join(directory_path, item)
                if os.path.isdir(full_path):
                    directories.append(f"📁 {item}/")
                else:
                    files.append(f"📄 {item}")
            
            # Sort and create output
            directories.sort()
            files.sort()
            
            result = f"Contents of directory '{directory_path}':\n\n"
            
            if directories:
                result += "Directories:\n" + "\n".join(directories) + "\n\n"
            
            if files:
                result += "Files:\n" + "\n".join(files)
            
            if not items:
                result += "Directory is empty."
            
            return result
            
        except PermissionError:
            return f"Error: Permission denied to access directory '{directory_path}'."
        except Exception as e:
            return f"Error accessing directory: {str(e)}"

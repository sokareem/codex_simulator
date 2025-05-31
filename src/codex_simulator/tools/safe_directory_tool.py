import os
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeDirectoryToolInput(BaseModel):
    """Input for the SafeDirectoryTool."""
    directory_path: str = Field(..., description="The path of the directory to read.")

class SafeDirectoryTool(BaseTool):
    """A tool to read directory contents with minimal restrictions."""
    name: str = "safe_directory_tool"
    description: str = "Lists files and subdirectories within a specified directory."
    args_schema: Type[BaseModel] = SafeDirectoryToolInput
    
    # Only block key system directories that could be problematic
    blocked_directories: List[str] = [
        "/etc/ssl", "/etc/ssh", "/root/.ssh", "/proc/kcore", 
        "/dev/mem", "/dev/kmem", "/dev/port"
    ]

    def _is_safe_path(self, path: str) -> dict:
        """Check if a path is safe to access."""
        # Convert to absolute path
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Check against blocked directories
        for blocked in self.blocked_directories:
            blocked_abs = os.path.abspath(os.path.expanduser(blocked))
            if abs_path.startswith(blocked_abs):
                return {"safe": False, "reason": f"Access to '{blocked}' is restricted for security reasons"}
        
        # Check if directory exists
        if not os.path.exists(abs_path):
            return {"safe": False, "reason": f"Directory '{abs_path}' does not exist"}
            
        # Check if it's actually a directory
        if not os.path.isdir(abs_path):
            return {"safe": False, "reason": f"Path '{abs_path}' is not a directory"}
                
        return {"safe": True, "reason": ""}

    def _run(self, directory_path: str) -> str:
        """List the contents of a directory if it passes safety checks."""
        safety_check = self._is_safe_path(directory_path)
        if not safety_check["safe"]:
            return f"Error: {safety_check['reason']}"
        
        try:
            abs_path = os.path.abspath(os.path.expanduser(directory_path))
            items = os.listdir(abs_path)
            
            # Categorize items as files or directories
            files = []
            directories = []
            
            for item in items:
                try:
                    full_path = os.path.join(abs_path, item)
                    if os.path.isdir(full_path):
                        directories.append(f"📁 {item}/")
                    else:
                        # Get file size
                        try:
                            size = os.path.getsize(full_path)
                            size_str = self._format_file_size(size)
                            files.append(f"📄 {item} ({size_str})")
                        except:
                            files.append(f"📄 {item}")
                except:
                    # In case of permission issues with specific files
                    files.append(f"❓ {item} (unable to access)")
            
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

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/1024/1024:.1f} MB"
        else:
            return f"{size_bytes/1024/1024/1024:.1f} GB"

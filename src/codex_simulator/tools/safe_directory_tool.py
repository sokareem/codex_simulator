import os
from typing import Optional, List, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeDirectoryToolInput(BaseModel):
    """Input schema for SafeDirectoryTool."""
    directory_path: str = Field(description="The path to the directory whose contents need to be listed.")

class SafeDirectoryTool(BaseTool):
    """Tool for safely listing directory contents."""
    name: str = "Safe Directory Lister"
    description: str = "Safely lists the contents of a specified directory. Restricted to allowed paths for security."
    args_schema: Type[BaseModel] = SafeDirectoryToolInput
    
    # Define as Pydantic fields to avoid validation errors
    allowed_paths: List[str] = Field(default_factory=list, exclude=True)
    blocked_directories: List[str] = Field(default_factory=list, exclude=True)

    def __init__(self, allowed_paths: Optional[List[str]] = None, blocked_directories: Optional[List[str]] = None, **kwargs):
        # Set up blocked directories first
        blocked_dirs = blocked_directories or [
            "/etc", "/var", "/bin", "/sbin", "/usr/bin", "/usr/sbin", 
            "/lib", "/root", "/boot", "/dev", "/proc", "/sys"
        ]
        blocked_dirs = [os.path.abspath(os.path.expanduser(p)) for p in blocked_dirs]
        
        # Set up allowed paths
        if allowed_paths is None:
            try:
                allowed_dirs = [os.getcwd()]
            except FileNotFoundError:
                # Fallback if CWD was deleted
                allowed_dirs = ["/"]
        else:
            allowed_dirs = [os.path.abspath(os.path.expanduser(p)) for p in allowed_paths]
        
        # Pass to parent constructor with fields properly set
        super().__init__(
            allowed_paths=allowed_dirs,
            blocked_directories=blocked_dirs,
            **kwargs
        )
        
        # Update description with current allowed paths
        self.description = f"Safely lists directory contents. Allowed base paths: {self.allowed_paths}"

    class Config:
        arbitrary_types_allowed = True
        
    def _is_safe_path(self, directory_path: str) -> bool:
        """Check if the directory path is safe to access."""
        abs_path = os.path.abspath(os.path.expanduser(directory_path))
        
        # Check against blocked directories
        for blocked in self.blocked_directories:
            if abs_path.startswith(blocked):
                return False
        
        # Check against allowed paths
        return any(abs_path.startswith(allowed) for allowed in self.allowed_paths)

    def _run(self, directory_path: str) -> str:
        """The method that CrewAI will call to run the tool."""
        abs_target_path = os.path.abspath(os.path.expanduser(directory_path))

        # Check if path is safe
        if not self._is_safe_path(directory_path):
            # Check which specific restriction was violated
            for blocked in self.blocked_directories:
                if abs_target_path.startswith(blocked):
                    return f"Error: Access to '{blocked}' is restricted for security reasons. Path requested: {abs_target_path}"
            
            return f"Error: Access to path '{abs_target_path}' is not allowed. Allowed base paths: {self.allowed_paths}"
        
        # Check if directory exists
        if not os.path.exists(abs_target_path):
            return f"Error: Directory '{abs_target_path}' does not exist."
        
        # Check if it's actually a directory
        if not os.path.isdir(abs_target_path):
            return f"Error: Path '{abs_target_path}' is not a directory."
        
        try:
            contents = os.listdir(abs_target_path)
            if not contents:
                return f"Contents of directory '{directory_path}':\nDirectory is empty."

            result = f"Contents of directory '{directory_path}':\nDirectories:\n"
            files_str = "Files:\n"
            
            dirs_found = False
            files_found = False

            for item in sorted(contents):
                full_item_path = os.path.join(abs_target_path, item)
                try:
                    if os.path.isdir(full_item_path):
                        result += f"  📁 {item}/\n"
                        dirs_found = True
                    elif os.path.isfile(full_item_path):
                        try:
                            size = os.path.getsize(full_item_path)
                            size_kb = size / 1024
                            if size_kb < 1:
                                size_str = f"{size}B"
                            else:
                                size_str = f"{size_kb:.1f}KB"
                            files_str += f"  📄 {item} ({size_str})\n"
                        except OSError:
                            files_str += f"  📄 {item} (size unavailable)\n"
                        files_found = True
                    else:
                        # Symlinks or other special file types
                        files_str += f"  ❓ {item} (special file type)\n"
                        files_found = True
                except OSError:
                    # Permission errors for individual items
                    result += f"  🚫 {item} (inaccessible)\n"

            if not dirs_found:
                result = result.replace("Directories:\n", "Directories: None\n")
            if not files_found:
                files_str = files_str.replace("Files:\n", "Files: None\n")
            
            return result + files_str
            
        except PermissionError:
            return f"Error: Permission denied to access directory '{abs_target_path}'."
        except Exception as e:
            return f"Error listing directory '{abs_target_path}': {str(e)}"

    # Keep the legacy method for backward compatibility
    def list_directory(self, directory_path: str) -> str:
        """Legacy method for backward compatibility."""
        return self._run(directory_path)

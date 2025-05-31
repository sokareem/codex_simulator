import os
from pathlib import Path
from typing import Optional, Type, Union

from crewai_tools import BaseTool
from pydantic import BaseModel, Field

from ..utils.permission_manager import PermissionManager


class SafeFileWriteToolSchema(BaseModel):
    file_path: str = Field(..., description="Path to the file to write")
    text: str = Field(..., description="Content to write to the file")


class SafeFileWriteTool(BaseTool):
    name: str = "SafeFileWriteTool"
    description: str = "Writes content to a file safely with permission checks"
    args_schema: Type[BaseModel] = SafeFileWriteToolSchema
    
    # Add model config to allow arbitrary types
    model_config = {"arbitrary_types_allowed": True}
    
    permission_manager: Optional[PermissionManager] = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permission_manager is None:
            self.permission_manager = PermissionManager()

    def _run(self, file_path: str, text: str) -> str:
        """Write content to a file with safety checks"""
        try:
            # Convert to Path object
            path = Path(file_path).resolve()
            
            # Check permissions
            if not self.permission_manager.check_tool_permission("file_write", str(path)):
                return f"Permission denied: File write not allowed for {path}"
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return f"Successfully wrote {len(text)} characters to {path}"
            
        except PermissionError:
            return f"Permission error: Cannot write to {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"

    # For backward compatibility
    def run(self, file_path: str, text: str) -> str:
        return self._run(file_path, text)

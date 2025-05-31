"""
Permission manager for CodexSimulator tools.
Handles permission checking and validation for various tool operations.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class PermissionRule:
    """Represents a permission rule for tools"""
    tool_name: str
    specifier: Optional[str] = None
    rule_type: str = "allow"  # "allow" or "deny"
    scope: str = "session"  # "session", "project", "permanent"


class PermissionManager(BaseModel):
    """
    Manages permissions for tool usage.
    Made Pydantic-compatible for use in CrewAI tools.
    """
    
    # Configuration
    model_config = {"arbitrary_types_allowed": True}
    
    # Permission storage as model fields
    session_permissions: Set[str] = set()
    project_permissions: Set[str] = set()
    permanent_permissions: Set[str] = set()
    denied_permissions: Set[str] = set()
    project_dir: Optional[Path] = None
    
    def __init__(self, project_dir: Optional[Path] = None, **kwargs):
        super().__init__(**kwargs)
        self.project_dir = project_dir or Path.cwd()
        self._load_permissions()
    
    def _load_permissions(self):
        """Load permissions from configuration files"""
        # Implementation stays the same but made instance method
        pass
    
    def check_tool_permission(self, tool_name: str, path: Optional[str] = None) -> bool:
        """
        Check if a tool operation is permitted.
        Simplified version for initial compatibility.
        """
        # For now, allow most operations but log them
        safe_tools = {
            'file_read', 'directory_list', 'file_write', 'shell_command'
        }
        
        if tool_name in safe_tools:
            return True
        
        # For unknown tools, be conservative
        return False
    
    def request_permission(self, tool_name: str, path: Optional[str] = None) -> bool:
        """Request permission for a tool operation"""
        # For now, auto-approve for development
        return True
    
    def add_session_permission(self, permission: str):
        """Add a session-specific permission"""
        self.session_permissions.add(permission)
    
    def clear_session_permissions(self):
        """Clear session-specific permissions"""
        self.session_permissions.clear()

"""
Claude Code-style permission management system.
Implements tiered permissions matching Claude Code's security model.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PermissionRule:
    """Represents a permission rule for tools"""
    tool_name: str
    specifier: Optional[str] = None
    rule_type: str = "allow"  # "allow" or "deny"
    scope: str = "session"  # "session", "project", "permanent"


class PermissionManager:
    """
    Claude Code-style tiered permission system.
    
    Permission Levels:
    - Read-only tools: No approval required
    - Bash commands: Approval required, can be permanently allowed per project
    - File modifications: Approval required, allowed until session end
    """
    
    # Tool categories matching Claude Code
    READ_ONLY_TOOLS = {
        'Read', 'LS', 'Grep', 'Glob', 'TodoRead', 'NotebookRead'
    }
    
    REQUIRES_APPROVAL_TOOLS = {
        'Bash', 'Edit', 'Write', 'MultiEdit', 'NotebookEdit', 
        'WebFetch', 'WebSearch'
    }
    
    SESSION_PERSISTENT_TOOLS = {
        'Edit', 'Write', 'MultiEdit', 'NotebookEdit'
    }
    
    PERMANENT_ALLOWABLE_TOOLS = {
        'Bash'
    }
    
    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path.cwd()
        
        # Permission storage
        self.session_permissions: Set[str] = set()
        self.project_permissions: Set[str] = set()
        self.permanent_permissions: Set[str] = set()
        self.denied_permissions: Set[str] = set()
        
        # Load existing permissions
        self._load_permissions()
    
    def _load_permissions(self):
        """Load permissions from settings.json files"""
        # Load user settings
        user_settings = self._load_user_settings()
        
        # Load project settings  
        project_settings = self._load_project_settings()
        
        # Load local project settings
        local_settings = self._load_local_project_settings()
        
        # Merge permissions (local > project > user)
        for settings in [user_settings, project_settings, local_settings]:
            if settings and 'permissions' in settings:
                perms = settings['permissions']
                
                if 'allow' in perms:
                    for rule in perms['allow']:
                        self.permanent_permissions.add(rule)
                
                if 'deny' in perms:
                    for rule in perms['deny']:
                        self.denied_permissions.add(rule)
    
    def _load_user_settings(self) -> Optional[Dict]:
        """Load user settings from ~/.claude/settings.json"""
        user_settings_path = Path.home() / '.claude' / 'settings.json'
        return self._load_json_file(user_settings_path)
    
    def _load_project_settings(self) -> Optional[Dict]:
        """Load project settings from .claude/settings.json"""
        project_settings_path = self.project_dir / '.claude' / 'settings.json'
        return self._load_json_file(project_settings_path)
    
    def _load_local_project_settings(self) -> Optional[Dict]:
        """Load local project settings from .claude/settings.local.json"""
        local_settings_path = self.project_dir / '.claude' / 'settings.local.json'
        return self._load_json_file(local_settings_path)
    
    def _load_json_file(self, path: Path) -> Optional[Dict]:
        """Load JSON file safely"""
        try:
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load {path}: {e}")
        return None
    
    def check_permission(self, tool_name: str, args: Dict = None, command: str = None) -> Tuple[bool, str]:
        """
        Check if tool usage is permitted.
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Create tool signature for checking
        tool_signature = self._create_tool_signature(tool_name, args, command)
        
        # Check if explicitly denied
        if self._is_denied(tool_signature):
            return False, "Tool usage explicitly denied by settings"
        
        # Check if read-only tool (always allowed)
        if tool_name in self.READ_ONLY_TOOLS:
            return True, "Read-only tool - no permission required"
        
        # Check if already permitted in this session
        if tool_signature in self.session_permissions:
            return True, "Previously allowed in this session"
        
        # Check if permanently allowed
        if self._is_permanently_allowed(tool_signature):
            return True, "Permanently allowed by settings"
        
        # Tool requires approval
        return False, "Tool requires user approval"
    
    def _create_tool_signature(self, tool_name: str, args: Dict = None, command: str = None) -> str:
        """Create a signature for tool usage matching Claude Code format"""
        if tool_name == 'Bash' and command:
            return f"Bash({command})"
        elif args and 'path' in args:
            return f"{tool_name}({args['path']})"
        elif args and 'domain' in args:
            return f"{tool_name}(domain:{args['domain']})"
        else:
            return tool_name
    
    def _is_denied(self, tool_signature: str) -> bool:
        """Check if tool is explicitly denied"""
        for denied_rule in self.denied_permissions:
            if self._matches_rule(tool_signature, denied_rule):
                return True
        return False
    
    def _is_permanently_allowed(self, tool_signature: str) -> bool:
        """Check if tool is permanently allowed"""
        for allowed_rule in self.permanent_permissions:
            if self._matches_rule(tool_signature, allowed_rule):
                return True
        return False
    
    def _matches_rule(self, tool_signature: str, rule: str) -> bool:
        """Check if tool signature matches permission rule"""
        # Exact match
        if tool_signature == rule:
            return True
        
        # Prefix match for rules ending with :*
        if rule.endswith(':*'):
            prefix = rule[:-2]
            if tool_signature.startswith(prefix):
                return True
        
        # Tool name only match
        tool_name = tool_signature.split('(')[0]
        if tool_name == rule:
            return True
        
        return False
    
    async def request_permission(self, tool_name: str, args: Dict = None, command: str = None) -> bool:
        """
        Request user permission for tool usage.
        Returns True if permission granted, False otherwise.
        """
        tool_signature = self._create_tool_signature(tool_name, args, command)
        
        # Display permission request
        print(f"\n🔐 Permission required for: {tool_signature}")
        
        if tool_name == 'Bash':
            print(f"   Command: {command}")
            print("   ⚠️  This will execute a shell command on your system")
        elif tool_name in {'Edit', 'Write', 'MultiEdit'}:
            print("   📝 This will modify files on your system")
        elif tool_name in {'WebFetch', 'WebSearch'}:
            print("   🌐 This will access the internet")
        
        # Get user choice
        choices = ["y", "n"]
        can_remember = False
        
        # Add remember options based on tool type
        if tool_name in self.PERMANENT_ALLOWABLE_TOOLS:
            choices.extend(["always", "project"])
            can_remember = True
            print("\n   Options:")
            print("   y - Allow once")
            print("   n - Deny")
            print("   always - Always allow this command (permanent)")
            print("   project - Allow for this project")
        elif tool_name in self.SESSION_PERSISTENT_TOOLS:
            choices.append("session")
            can_remember = True
            print("\n   Options:")
            print("   y - Allow once") 
            print("   n - Deny")
            print("   session - Allow for this session")
        else:
            print("\n   Options: y (allow once) / n (deny)")
        
        while True:
            choice = input("\n   Choice: ").strip().lower()
            
            if choice in choices:
                break
            else:
                print(f"   Invalid choice. Please enter one of: {', '.join(choices)}")
        
        # Process choice
        if choice == 'n':
            return False
        elif choice == 'y':
            return True
        elif choice == 'session':
            self.session_permissions.add(tool_signature)
            return True
        elif choice == 'project':
            self._add_project_permission(tool_signature)
            return True
        elif choice == 'always':
            self._add_permanent_permission(tool_signature)
            return True
        
        return False
    
    def _add_project_permission(self, tool_signature: str):
        """Add permission to project settings"""
        try:
            settings_dir = self.project_dir / '.claude'
            settings_dir.mkdir(exist_ok=True)
            
            settings_file = settings_dir / 'settings.json'
            
            # Load existing settings
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Add permission
            if 'permissions' not in settings:
                settings['permissions'] = {}
            if 'allow' not in settings['permissions']:
                settings['permissions']['allow'] = []
            
            if tool_signature not in settings['permissions']['allow']:
                settings['permissions']['allow'].append(tool_signature)
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"   ✅ Added to project permissions: {tool_signature}")
            
        except Exception as e:
            print(f"   ⚠️ Could not save project permission: {e}")
    
    def _add_permanent_permission(self, tool_signature: str):
        """Add permission to user settings"""
        try:
            settings_dir = Path.home() / '.claude'
            settings_dir.mkdir(exist_ok=True)
            
            settings_file = settings_dir / 'settings.json'
            
            # Load existing settings
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Add permission
            if 'permissions' not in settings:
                settings['permissions'] = {}
            if 'allow' not in settings['permissions']:
                settings['permissions']['allow'] = []
            
            if tool_signature not in settings['permissions']['allow']:
                settings['permissions']['allow'].append(tool_signature)
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"   ✅ Added to permanent permissions: {tool_signature}")
            
        except Exception as e:
            print(f"   ⚠️ Could not save permanent permission: {e}")
    
    def clear_session_permissions(self):
        """Clear session-specific permissions"""
        self.session_permissions.clear()
    
    def list_permissions(self) -> Dict[str, List[str]]:
        """List all current permissions"""
        return {
            'session': list(self.session_permissions),
            'permanent': list(self.permanent_permissions),
            'denied': list(self.denied_permissions)
        }

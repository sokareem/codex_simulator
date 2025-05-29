import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class LocationData:
    """Structured data for geographic location."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    source: Optional[str] = None  # e.g., "user_provided", "gps", "ip"
    timestamp: Optional[datetime] = None # type: ignore
    accuracy: Optional[float] = None # in meters

@dataclass
class SessionState:
    """Structured state management for terminal sessions"""
    cwd: str
    command_history: List[Dict]
    context_data: Dict[str, Any]
    user_preferences: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_log: List[Dict]
    current_location: Optional[LocationData] = None
    location_permission: str = "denied"  # "denied", "session", "always"
    named_locations: Dict[str, LocationData] = field(default_factory=dict)
    
    def update_from_crew_result(self, crew_result: Any) -> None:
        """Update state based on crew execution results"""
        # Extract CWD changes
        if hasattr(crew_result, 'cwd_update'):
            self.cwd = crew_result.cwd_update
        
        # Extract performance metrics
        if hasattr(crew_result, 'metrics'):
            self.performance_metrics.update(crew_result.metrics)
        
        # Log any errors
        if hasattr(crew_result, 'errors'):
            self.error_log.extend(crew_result.errors)

class FlowStateManager:
    """Advanced state management for flows"""
    
    def __init__(self):
        self.session_state = SessionState(
            cwd=os.getcwd(),
            command_history=[],
            context_data={},
            user_preferences={},
            performance_metrics={},
            error_log=[],
            current_location=None,
            location_permission="denied",
            named_locations={}
        )
    
    def create_crew_context(self, command_type: str) -> Dict[str, Any]:
        """Create optimized context for specific crew types"""
        base_context = {
            'cwd': self.session_state.cwd,
            'recent_commands': self.session_state.command_history[-5:],
            'user_preferences': self.session_state.user_preferences,
            'current_location': self.session_state.current_location if self.session_state.location_permission != "denied" else None,
            'location_permission': self.session_state.location_permission
        }
        
        if command_type == 'file_ops':
            base_context['file_cache'] = self._get_file_cache()
        elif command_type == 'code_exec':
            base_context['safety_settings'] = self._get_safety_settings()
        
        return base_context
    
    def _get_file_cache(self) -> Dict[str, Any]:
        """Get file system cache"""
        return {}
    
    def _get_safety_settings(self) -> Dict[str, Any]:
        """Get safety settings for code execution"""
        return {
            'max_execution_time': 60,
            'allowed_commands': ['python', 'pip', 'echo']
        }

    def set_current_location(self, location_data: LocationData, source: str = "user_provided"):
        """Sets or updates the current location."""
        from datetime import datetime # Local import
        location_data.source = source
        location_data.timestamp = datetime.now()
        self.session_state.current_location = location_data
        if self.session_state.location_permission == "denied": # auto-allow for session if user sets it
            self.session_state.location_permission = "session"

    def get_current_location(self) -> Optional[LocationData]:
        """Retrieves the current location if permission is granted."""
        if self.session_state.location_permission != "denied":
            return self.session_state.current_location
        return None

    def set_location_permission(self, permission: str):
        """Sets the location permission level."""
        if permission in ["denied", "session", "always"]:
            self.session_state.location_permission = permission
            if permission == "denied":
                self.session_state.current_location = None # Clear location if denied
        else:
            raise ValueError("Invalid permission level. Must be 'denied', 'session', or 'always'.")

    def get_location_permission(self) -> str:
        """Gets the current location permission level."""
        return self.session_state.location_permission

    def add_named_location(self, name: str, location_data: LocationData):
        """Adds or updates a named location."""
        self.session_state.named_locations[name.lower()] = location_data

    def get_named_location(self, name: str) -> Optional[LocationData]:
        """Retrieves a named location."""
        return self.session_state.named_locations.get(name.lower())

    def clear_current_location(self):
        """Clears the current location, e.g., at session end if permission is 'session'."""
        self.session_state.current_location = None
        if self.session_state.location_permission == "session":
            self.session_state.location_permission = "denied" # Reset session permission
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class SessionState:
    """Structured state management for terminal sessions"""
    cwd: str
    command_history: List[Dict]
    context_data: Dict[str, Any]
    user_preferences: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_log: List[Dict]
    
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
            error_log=[]
        )
    
    def create_crew_context(self, command_type: str) -> Dict[str, Any]:
        """Create optimized context for specific crew types"""
        base_context = {
            'cwd': self.session_state.cwd,
            'recent_commands': self.session_state.command_history[-5:],
            'user_preferences': self.session_state.user_preferences
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
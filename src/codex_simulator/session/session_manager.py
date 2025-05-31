"""
Session management for Claude Code-style interface.
Handles conversation history, context tracking, and session persistence.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class SessionManager:
    """
    Manages conversation sessions and context tracking.
    Provides session persistence and conversation history management.
    """
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        self.sessions_dir = sessions_dir or (Path.home() / '.claude' / 'sessions')
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session tracking
        self.current_session: Optional[str] = None
        self.session_data: Dict[str, Any] = {}
        
        # Cleanup old sessions periodically
        self._cleanup_old_sessions()
    
    def create_new_session(self) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())[:8]  # Short ID like Claude Code
        
        self.current_session = session_id
        self.session_data = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'working_directory': str(Path.cwd()),
            'conversation': [],
            'context_updates': [],
            'tool_usage': []
        }
        
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            with open(session_file, 'r') as f:
                self.session_data = json.load(f)
            
            self.current_session = session_id
            return True
            
        except Exception as e:
            print(f"⚠️ Could not load session {session_id}: {e}")
            return False
    
    def save_session(self, session_id: Optional[str] = None) -> bool:
        """Save current session to disk"""
        if not session_id:
            session_id = self.current_session
        
        if not session_id or not self.session_data:
            return False
        
        session_file = self.sessions_dir / f"{session_id}.json"
        
        try:
            # Update last modified
            self.session_data['last_modified'] = datetime.now().isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Could not save session: {e}")
            return False
    
    def add_conversation_entry(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add an entry to the conversation history"""
        if not self.session_data:
            return
        
        entry = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.session_data['conversation'].append(entry)
        
        # Auto-save periodically
        if len(self.session_data['conversation']) % 10 == 0:
            self.save_session()
    
    def add_tool_usage(self, tool_name: str, args: Dict, result: Any, success: bool = True):
        """Track tool usage in the session"""
        if not self.session_data:
            return
        
        tool_entry = {
            'tool': tool_name,
            'args': args,
            'result': str(result)[:1000],  # Truncate large results
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.session_data['tool_usage'].append(tool_entry)
    
    def update_session_context(self, session_id: str, command: str, response: str):
        """Update session context with new command/response pair"""
        if session_id != self.current_session:
            return
        
        context_update = {
            'command': command,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'working_directory': str(Path.cwd())
        }
        
        self.session_data['context_updates'].append(context_update)
        
        # Keep only last 20 context updates to prevent bloat
        if len(self.session_data['context_updates']) > 20:
            self.session_data['context_updates'] = self.session_data['context_updates'][-20:]
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for current session"""
        if not self.session_data or 'conversation' not in self.session_data:
            return []
        
        conversation = self.session_data['conversation']
        
        if limit:
            return conversation[-limit:]
        
        return conversation
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.session_data:
            return {}
        
        return {
            'id': self.session_data.get('id'),
            'created_at': self.session_data.get('created_at'),
            'working_directory': self.session_data.get('working_directory'),
            'conversation_length': len(self.session_data.get('conversation', [])),
            'tools_used': len(self.session_data.get('tool_usage', [])),
            'last_activity': self._get_last_activity_time()
        }
    
    def _get_last_activity_time(self) -> Optional[str]:
        """Get timestamp of last activity in session"""
        if not self.session_data:
            return None
        
        conversation = self.session_data.get('conversation', [])
        if conversation:
            return conversation[-1].get('timestamp')
        
        return self.session_data.get('created_at')
    
    def list_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """List recent sessions"""
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    'id': session_data.get('id'),
                    'created_at': session_data.get('created_at'),
                    'last_modified': session_data.get('last_modified'),
                    'working_directory': session_data.get('working_directory'),
                    'conversation_length': len(session_data.get('conversation', []))
                })
                
            except Exception:
                continue
        
        # Sort by last modified time
        sessions.sort(key=lambda x: x.get('last_modified', x.get('created_at', '')), reverse=True)
        
        return sessions[:limit]
    
    def get_most_recent_session_id(self) -> Optional[str]:
        """Get the ID of the most recent session in current directory"""
        cwd = str(Path.cwd())
        recent_sessions = self.list_recent_sessions()
        
        for session in recent_sessions:
            if session.get('working_directory') == cwd:
                return session.get('id')
        
        return None
    
    def _cleanup_old_sessions(self, days_to_keep: int = 30):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                # Check file modification time
                if session_file.stat().st_mtime < cutoff_date.timestamp():
                    session_file.unlink()
                    
            except Exception:
                continue
    
    def compact_session(self, session_id: Optional[str] = None, instructions: str = ""):
        """
        Compact session conversation history.
        In a full implementation, this would use LLM to summarize.
        """
        if not session_id:
            session_id = self.current_session
        
        if not session_id or session_id != self.current_session:
            return False
        
        conversation = self.session_data.get('conversation', [])
        
        if len(conversation) <= 10:
            print("📝 Session is already compact (≤10 messages)")
            return True
        
        # Simple compaction - keep first and last 5 messages
        # In practice, you'd use LLM to create a summary
        first_messages = conversation[:5]
        last_messages = conversation[-5:]
        
        summary_entry = {
            'role': 'system',
            'content': f"[Session compacted - {len(conversation) - 10} messages summarized]\n{instructions}",
            'timestamp': datetime.now().isoformat(),
            'metadata': {'type': 'compaction_summary'}
        }
        
        self.session_data['conversation'] = first_messages + [summary_entry] + last_messages
        
        print(f"📝 Compacted session from {len(conversation)} to {len(self.session_data['conversation'])} messages")
        
        return self.save_session(session_id)

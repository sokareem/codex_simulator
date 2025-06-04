import threading
import time
import signal
import sys
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass 
class ExecutionState:
    """Track execution state for safe termination"""
    is_running: bool = False
    stop_requested: bool = False
    current_task: Optional[str] = None
    execution_thread: Optional[threading.Thread] = None

class TerminalUI:
    """CLI Terminal UI with stop generation capability"""
    
    def __init__(self, codex_simulator=None):
        self.execution_state = ExecutionState()
        self.codex_simulator = codex_simulator
        self.original_sigint_handler = None
        
    def setup_stop_handling(self):
        """Setup CLI stop handling with Ctrl+C"""
        self.original_sigint_handler = signal.signal(signal.SIGINT, self._handle_stop_request)
        
    def cleanup_stop_handling(self):
        """Restore original signal handler"""
        if self.original_sigint_handler:
            signal.signal(signal.SIGINT, self.original_sigint_handler)
    
    def _handle_stop_request(self, signum, frame):
        """Handle stop request via Ctrl+C"""
        if self.execution_state.is_running:
            print("\n🛑 Stop requested - Safely terminating execution...")
            self.execution_state.stop_requested = True
            
            if self.codex_simulator:
                self.codex_simulator.execution_state.stop_requested = True
                
            # Give some time for graceful shutdown
            threading.Timer(3.0, self._force_stop_if_needed).start()
        else:
            print("\n👋 Exiting...")
            sys.exit(0)
    
    def _force_stop_if_needed(self):
        """Force stop if graceful shutdown takes too long"""
        if self.execution_state.is_running and self.execution_state.stop_requested:
            print("⚠️ Force stopping execution...")
            self.execution_state.is_running = False
            # In extreme cases, we could force exit, but let's be gentle
    
    def display_status(self):
        """Display current execution status"""
        if self.execution_state.is_running:
            task = self.execution_state.current_task or "Unknown task"
            print(f"📊 Status: Executing '{task}' (Ctrl+C to stop)")
        else:
            print("📊 Status: Ready for commands")
    
    def start_execution_monitoring(self, command: str):
        """Start monitoring execution state"""
        self.execution_state.is_running = True
        self.execution_state.stop_requested = False  
        self.execution_state.current_task = command
        
    def end_execution_monitoring(self):
        """End execution monitoring"""
        self.execution_state.is_running = False
        self.execution_state.stop_requested = False
        self.execution_state.current_task = None

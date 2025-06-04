from flask import Flask, request, jsonify, render_template
import threading
import time
from typing import Dict, Optional
import uuid

class TerminalAPI:
    """API endpoints for terminal interface with stop functionality"""
    
    def __init__(self, codex_simulator):
        self.app = Flask(__name__)
        self.codex_simulator = codex_simulator
        self.active_executions: Dict[str, threading.Thread] = {}
        self.execution_results: Dict[str, str] = {}
        self.stop_requests: Dict[str, bool] = {}
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes with stop functionality"""
        
        @self.app.route('/')
        def index():
            return render_template('terminal_interface.html')
        
        @self.app.route('/execute', methods=['POST'])
        def execute_command():
            data = request.json
            command = data.get('command', '').strip()
            execution_id = str(data.get('execution_id', uuid.uuid4()))
            
            if not command:
                return jsonify({'error': 'No command provided'}), 400
            
            # Check if already executing
            if execution_id in self.active_executions:
                return jsonify({'error': 'Execution already in progress'}), 409
            
            # Start execution in background thread
            execution_thread = threading.Thread(
                target=self._execute_with_monitoring,
                args=(command, execution_id)
            )
            
            self.active_executions[execution_id] = execution_thread
            self.stop_requests[execution_id] = False
            
            execution_thread.start()
            
            # Wait for completion or timeout
            return self._wait_for_result(execution_id, timeout=300)
        
        @self.app.route('/stop', methods=['POST'])
        def stop_execution():
            data = request.json
            execution_id = str(data.get('execution_id', ''))
            
            if execution_id in self.stop_requests:
                self.stop_requests[execution_id] = True
                
                # Set stop request in codex simulator
                self.codex_simulator.execution_state.stop_requested = True
                
                return jsonify({
                    'message': '🛑 Stop request sent - execution will terminate safely',
                    'execution_id': execution_id
                })
            else:
                return jsonify({'error': 'No active execution found'}), 404
    
    def _execute_with_monitoring(self, command: str, execution_id: str):
        """Execute command with stop monitoring"""
        try:
            # Set execution state
            self.codex_simulator.execution_state.stop_requested = False
            
            # Execute command
            result = self.codex_simulator.terminal_assistant_sync(command)
            
            # Store result
            if self.stop_requests.get(execution_id, False):
                self.execution_results[execution_id] = "🛑 Execution stopped by user"
            else:
                self.execution_results[execution_id] = result
                
        except Exception as e:
            self.execution_results[execution_id] = f"❌ Execution error: {str(e)}"
        finally:
            # Cleanup
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    def _wait_for_result(self, execution_id: str, timeout: int = 300):
        """Wait for execution result with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if execution completed
            if execution_id in self.execution_results:
                result = self.execution_results.pop(execution_id)
                
                # Cleanup
                if execution_id in self.stop_requests:
                    del self.stop_requests[execution_id]
                
                return jsonify({'result': result, 'execution_id': execution_id})
            
            # Check if stop was requested
            if self.stop_requests.get(execution_id, False):
                return jsonify({
                    'result': '🛑 Execution stopped by user', 
                    'execution_id': execution_id
                })
            
            time.sleep(0.1)
        
        # Timeout
        return jsonify({'error': 'Execution timeout'}), 408
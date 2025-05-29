import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from crewai.flow import Flow, start, listen, router, or_
from crewai import Crew

# Define the state model with Pydantic
class TerminalState(BaseModel):
    cwd: str = os.getcwd()
    command_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    session_data: Dict[str, Any] = {}

# Make the flow generic over this state type
class TerminalAssistantFlow(Flow[TerminalState]):
    """Main flow orchestrating terminal assistant operations"""
    
    def __init__(self):
        # Initialize with proper Flow state management
        super().__init__()
        # Don't directly assign state - let Flow manage it
    
    @start()
    def parse_command(self) -> Dict[str, Any]: # Modified return type
        """Initial command parsing, intent classification, and orchestration of handling."""
        command = getattr(self, '_input_command', '')
        intent = self._classify_intent(command)
        
        # Store command data in instance for other methods to access
        self._current_command = command
        self._current_intent = intent
        self._current_timestamp = datetime.now()
        
        # Enhanced routing based on improved classification
        routing_map = {
            'simple_query': 'handle_simple_query',
            'file_ops': 'delegate_to_file_crew',
            'code_exec': 'delegate_to_code_crew', 
            'web_search': 'delegate_to_web_crew',
            'system_introspection': 'handle_system_introspection',
            'code_analysis': 'handle_code_analysis',
            'multi_step_workflow': 'handle_multi_step_workflow',
            'system_monitoring': 'handle_system_monitoring',
            'complex_query': 'handle_complex_query',
            'needs_clarification': 'request_clarification'
        }
        
        target_method_name = routing_map.get(intent, 'handle_complex_query')

        # Get the actual handler method from self
        # Default to handle_complex_query if the name is not found, though it should always be in routing_map
        handler_method = getattr(self, target_method_name, self.handle_complex_query)
        
        # Call the selected handler method
        # Each handler method is expected to return a dictionary
        handler_result_dict = handler_method()
        
        # Pass the handler's result to the format_response method
        # format_response also returns a dictionary, which should be the final output of the flow
        final_output_dict = self.format_response(handler_result_dict)
        
        return final_output_dict # Return the fully processed dictionary
    
    def _classify_intent(self, command: str) -> str:
        """Enhanced intent classification with meta-analysis and multi-step detection"""
        command_lower = command.lower().strip()
        
        # Basic check for vagueness (example, can be more sophisticated)
        if len(command_lower.split()) < 2 and command_lower not in ['ls', 'pwd', 'help', 'df', 'top', 'exit', 'quit']:
             if not any(kw in command_lower for kw in ['list', 'show', 'what', 'how', 'explain', 'run', 'execute', 'search', 'find', 'analyze', 'monitor', 'cd', 'cat']):
                return 'needs_clarification'

        # System introspection queries (highest priority)
        system_keywords = ['delegation', 'agent', 'flow', 'crew', 'architecture', 'system', 'mechanism', 'specialist']
        introspection_keywords = ['how does', 'what happens', 'explain', 'walk me through', 'map the data flow']
        
        if any(keyword in command_lower for keyword in introspection_keywords) and \
           any(keyword in command_lower for keyword in system_keywords):
            return 'system_introspection'
        
        # Code analysis queries
        analysis_keywords = ['analyze', 'debug', 'explain code', 'function', 'snippet', 'terminal_flow.py']
        if any(keyword in command_lower for keyword in analysis_keywords) and \
           ('code' in command_lower or '.py' in command_lower or 'function' in command_lower):
            return 'code_analysis'
        
        # Multi-step workflow queries
        workflow_keywords = ['workflow', 'create and', 'search and', 'count and', 'save to']
        multi_step_indicators = [' and ', ' then ', ';', '&&']
        
        if any(keyword in command_lower for keyword in workflow_keywords) or \
           any(indicator in command for indicator in multi_step_indicators):
            return 'multi_step_workflow'
        
        # Performance and system monitoring
        performance_keywords = ['processes', 'memory', 'disk space', 'performance', 'running', 'system info']
        if any(keyword in command_lower for keyword in performance_keywords):
            return 'system_monitoring'
        
        # File operations (expanded patterns)
        file_ops_keywords = ['ls', 'cd', 'pwd', 'cat', 'find', 'grep', 'mkdir', 'touch', 'directory', 'files', 'size']
        if any(keyword in command_lower for keyword in file_ops_keywords):
            return 'file_ops'
        
        # Code execution
        code_exec_keywords = ['python', 'pip', 'node', 'npm', 'execute', 'run', 'script']
        if any(keyword in command_lower for keyword in code_exec_keywords):
            return 'code_exec'
        
        # Web search
        web_keywords = ['search', 'find information', 'web', 'research', 'online']
        if any(keyword in command_lower for keyword in web_keywords):
            return 'web_search'
        
        # Help/commands
        help_keywords = ['help', 'commands', 'available', 'what can you do', 'capabilities']
        if any(keyword in command_lower for keyword in help_keywords):
            return 'simple_query'
        
        # If no other intent matches and it's not obviously vague, treat as complex.
        # The vagueness check above should catch some unclear short commands.
        return 'complex_query'
    
    @listen('handle_simple_query')
    def handle_simple_query(self) -> Dict[str, Any]:
        """Handle simple queries directly"""
        command = self._current_command
        if 'help' in command.lower() or 'commands' in command.lower():
            response = self._get_available_commands()
        elif 'pwd' in command.lower() or 'current directory' in command.lower():
            response = f"Current directory: {os.getcwd()}"
        elif any(keyword in command.lower() for keyword in ['disk space', 'df', 'free space', 'partition']):
            response = self._handle_system_info_query(command)
        else:
            response = "I can help you with file operations, code execution, and web searches. Type 'help' for available commands."
        
        return {
            'command': command,
            'result': response,
            'intent': self._current_intent,
            'timestamp': self._current_timestamp
        }

    @listen('delegate_to_file_crew')
    def delegate_to_file_crew(self) -> Dict[str, Any]:
        """Delegate file operations to specialized crew"""
        from .crew_factories import CrewFactory
        
        try:
            state_context = {
                'command': self._current_command,
                'cwd': os.getcwd(),
                # 'context': self.state.context # Pass flow's context if needed by crew
            }
            file_crew = CrewFactory.create_file_operations_crew(state_context)
            # Inputs for kickoff can be used if task description has placeholders like {some_context_var}
            crew_result = file_crew.kickoff(inputs={'flow_context': self.state.context}) 
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in file operations: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('delegate_to_code_crew')
    def delegate_to_code_crew(self) -> Dict[str, Any]:
        """Delegate code execution to specialized crew"""
        from .crew_factories import CrewFactory
        
        try:
            # Pass command and safety_checks directly to the factory method
            code_crew = CrewFactory.create_code_execution_crew(
                command=self._current_command,
                safety_checks=True # Example, could be configurable
            )
            crew_result = code_crew.kickoff(inputs={'flow_context': self.state.context})
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in code execution: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('delegate_to_web_crew')
    def delegate_to_web_crew(self) -> Dict[str, Any]:
        """Delegate web research to specialized crew"""
        from .crew_factories import CrewFactory
        
        try:
            web_crew = CrewFactory.create_research_crew(query=self._current_command)
            crew_result = web_crew.kickoff(inputs={'flow_context': self.state.context})
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in web research: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('handle_complex_query')
    def handle_complex_query(self) -> Dict[str, Any]:
        """Handle complex queries that might need multiple crews or clarification."""
        # Check if it's complex or just unclassified and potentially vague
        if len(self._current_command.split()) < 3 and not any(kw in self._current_command.lower() for kw in [' and ', ' then ', ';']):
            # Potentially vague, ask for clarification
            return self.request_clarification()

        # For truly complex queries, provide a helpful response
        response = f"I understand you want to: {self._current_command}\n\n"
        response += "I can help with file operations, code execution, and web searches. "
        response += "Could you break this down into more specific tasks?"
        
        return {
            'command': self._current_command,
            'result': response,
            'intent': self._current_intent,
            'timestamp': self._current_timestamp
        }

    @listen('handle_system_introspection')
    def handle_system_introspection(self) -> Dict[str, Any]:
        """Handle questions about the system's own architecture and delegation"""
        command = self._current_command
        command_lower = command.lower()
        
        if 'delegation' in command_lower and ('mechanism' in command_lower or 'how does' in command_lower):
            response = self._explain_delegation_mechanism()
        elif 'data flow' in command_lower or 'map the' in command_lower:
            response = self._explain_data_flow()
        elif 'state' in command_lower and ('maintain' in command_lower or 'remember' in command_lower):
            response = self._explain_state_management()
        elif 'flow' in command_lower and 'crew' in command_lower:
            response = self._explain_flow_vs_crew()
        elif 'complex task' in command_lower and 'delegate' in command_lower:
            response = self._explain_complex_task_delegation()
        else:
            response = self._explain_system_architecture()
        
        return {
            'command': command,
            'result': response,
            'intent': self._current_intent,
            'timestamp': self._current_timestamp
        }

    @listen('handle_code_analysis')
    def handle_code_analysis(self) -> Dict[str, Any]:
        """Handle code analysis and debugging queries"""
        from .crew_factories import CrewFactory
        
        try:
            # Create specialized crew for code analysis
            code_crew = CrewFactory.create_code_analysis_crew(
                command=self._current_command,
                analysis_type='code_review' # Example, could be dynamic
            )
            crew_result = code_crew.kickoff(inputs={'flow_context': self.state.context})
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in code analysis: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('handle_multi_step_workflow')
    def handle_multi_step_workflow(self) -> Dict[str, Any]:
        """Handle complex multi-step workflows requiring multiple crews"""
        from .crew_factories import CrewFactory
        
        try:
            # Create orchestrated workflow crew
            workflow_crew = CrewFactory.create_workflow_crew(
                command=self._current_command,
                workflow_type='multi_step', # Example
                current_directory=os.getcwd()
            )
            crew_result = workflow_crew.kickoff(inputs={'flow_context': self.state.context})
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in workflow execution: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('handle_system_monitoring')
    def handle_system_monitoring(self) -> Dict[str, Any]:
        """Handle system monitoring and performance queries"""
        from .crew_factories import CrewFactory
        
        try:
            # Create system monitoring crew
            monitoring_crew = CrewFactory.create_system_monitoring_crew(
                command=self._current_command,
                monitoring_type='system_info' # Example
            )
            crew_result = monitoring_crew.kickoff(inputs={'flow_context': self.state.context})
            
            return {
                'command': self._current_command,
                'result': crew_result,
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }
        except Exception as e:
            return {
                'command': self._current_command,
                'result': f"Error in system monitoring: {str(e)}",
                'intent': self._current_intent,
                'timestamp': self._current_timestamp
            }

    @listen('needs_clarification')
    def request_clarification(self) -> Dict[str, Any]:
        """Ask the user for clarification on a vague command."""
        # More sophisticated logic could be added here, e.g., using an LLM to formulate the question
        clarification_question = (
            f"Your command '{self._current_command}' is a bit unclear. "
            "Could you please provide more details or rephrase your request?"
        )
        return {
            'command': self._current_command,
            'result': clarification_question,
            'intent': 'clarification_request', # Custom intent to signal this state
            'timestamp': self._current_timestamp,
            'clarification_needed': True # Flag for the calling system
        }

    @listen(or_('handle_simple_query', 'delegate_to_file_crew', 'delegate_to_code_crew', 'delegate_to_web_crew', 'handle_complex_query', 'handle_system_introspection', 'handle_code_analysis', 'handle_multi_step_workflow', 'handle_system_monitoring', 'needs_clarification'))
    def format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format and structure the final response"""
        formatted_response = self._format_terminal_response(result)
        
        return {
            'response': formatted_response,
            'session_complete': True
        }
    
    def _update_state_from_crew_result(self, crew_result: Any) -> None:
        """Update state based on crew execution results"""
        # Extract CWD changes if present
        if hasattr(crew_result, 'cwd_update'):
            self.state.cwd = crew_result.cwd_update
        
        # Extract any context updates
        if hasattr(crew_result, 'context_update'):
            new_context = self.state.context.copy()
            new_context.update(crew_result.context_update)
            self.state.context = new_context
    
    def _extract_metrics(self, crew_result: Any) -> Dict[str, Any]:
        """Extract performance metrics from crew results"""
        return {
            'execution_time': getattr(crew_result, 'execution_time', 0),
            'success': getattr(crew_result, 'success', True),
            'error_count': getattr(crew_result, 'error_count', 0)
        }
    
    def _format_terminal_response(self, result: Dict[str, Any]) -> str:
        """Format the response for terminal output"""
        if isinstance(result.get('result'), str):
            return result['result']
        elif hasattr(result.get('result'), 'raw_output'):
            return str(result['result'].raw_output)
        else:
            return str(result.get('result', 'No response generated'))
    
    def _get_available_commands(self) -> str:
        """Return available commands information"""
        return """
# Available Commands in Claude Terminal Assistant

## File Navigation & System Info Commands
- `ls [directory]` - List files and directories
- `pwd` - Show current directory
- `cd [directory]` - Change current working directory
- `cat [file]` - Display file contents
- `find [pattern]` - Search for files by pattern

## Code Execution Commands
- `python [file.py]` - Run Python file
- `pip install [package]` - Install Python package
- `echo [text]` - Print text to output

## Special Commands
- `search [query]` - Search the web for information
- `help` or `commands` - Show this list of commands

## Natural Language Interface
You can also use natural language queries like:
- "Show files in current directory"
- "What's in this directory?"
- "Read the file README.md"

"""
    
    def _handle_system_info_query(self, command: str) -> str:
        """Handle system information queries like disk space"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ['disk space', 'df', 'free space']):
            return "To check disk space, you can use the command: df -h\nThis will show disk usage in human-readable format."
        elif 'partition' in command_lower:
            return "To see partition information, you can use: df -h or diskutil list (on macOS)\nThese commands will show how your drive is partitioned."
        else:
            return "I can help you check system information. Try asking about disk space or partitions specifically."
    
    def _explain_delegation_mechanism(self) -> str:
        """Explain how the delegation system works"""
        return """## Agent Delegation Mechanism

The terminal assistant uses a hierarchical delegation system with the following logic:

**1. Intent Classification**: Commands are analyzed for keywords and patterns to determine which specialist can handle them.

**2. Prioritization Logic**: When multiple specialists could handle a task:
   - **File operations** (ls, cd, find) → FileNavigator
   - **Code execution** (python, pip, npm) → CodeExecutor  
   - **Information gathering** (search, research) → WebResearcher
   - **System analysis** → Performance Monitor

**3. Delegation Process**:
   - Terminal Commander analyzes the request
   - Identifies required specialist(s)
   - Delegates via DelegateTool with clear task description
   - Receives results and synthesizes response

**4. Multi-Agent Coordination**: For complex tasks requiring multiple specialists, the Terminal Commander orchestrates sequential delegation and combines results.

**5. Fallback Mechanism**: If delegation fails, the system falls back to crew-only mode or provides helpful guidance."""

    def _explain_data_flow(self) -> str:
        """Explain the complete data flow from input to response"""
        return """## Data Flow Architecture

**Input → Classification → Routing → Execution → Response**

1. **Command Input**: User enters command in terminal
2. **Flow Parsing**: TerminalAssistantFlow.parse_command() classifies intent
3. **Intent Routing**: Based on classification, routes to appropriate handler:
   - Simple queries → handle_simple_query
   - File ops → delegate_to_file_crew
   - Code execution → delegate_to_code_crew
   - Web research → delegate_to_web_crew
   - System introspection → handle_system_introspection

4. **Crew Creation**: CrewFactory creates specialized crew with appropriate agents
5. **Task Execution**: Specialist agents use their tools to complete tasks
6. **Result Aggregation**: Results flow back through the delegation chain
7. **Response Formatting**: format_response() structures output for terminal
8. **State Updates**: System updates working directory, command history, and CLAUDE.md

**State Persistence**: The StateTracker maintains context across commands, including current directory and command history."""

    def _explain_state_management(self) -> str:
        """Explain how state is maintained between commands"""
        return """## State Management System

**Yes, directory changes and context are preserved between commands.**

**State Components**:
- **Current Working Directory**: Tracked via StateTracker, updated after cd commands
- **Command History**: All commands stored in memory and CLAUDE.md
- **Session Context**: Persistent across the terminal session
- **CLAUDE.md File**: Shared memory file updated after each command

**State Persistence Mechanisms**:
1. **StateTracker Class**: Maintains in-memory state during session
2. **Directory Tracking**: CWD changes detected from command responses and updated
3. **Context Propagation**: Previous commands and results inform future operations
4. **File-Based Memory**: CLAUDE.md serves as persistent memory between sessions

**Example**: If you run `cd /tmp`, the next command will execute in /tmp context, and this change is remembered for all subsequent commands in the session."""

    def _explain_flow_vs_crew(self) -> str:
        """Compare flow orchestration vs crew-only modes"""
        return """## Flow vs Crew Orchestration Modes

**Flow Orchestration Mode** (Current):
- **Advantages**: Intelligent routing, better error handling, state management
- **Best for**: Simple commands, well-defined operations, rapid responses
- **Process**: Command → Intent Classification → Specialized Handler → Response

**Crew-Only Mode** (Fallback):
- **Advantages**: Full agent collaboration, complex reasoning, hierarchical delegation
- **Best for**: Complex multi-step tasks, ambiguous requests, creative problem-solving
- **Process**: Command → Terminal Commander → Multi-Agent Collaboration → Response

**When to Use Each**:
- **Flow Mode**: File operations, system commands, straightforward queries
- **Crew Mode**: "Analyze this codebase and suggest improvements", complex workflows
- **Hybrid Approach**: System automatically falls back from Flow to Crew for complex tasks

**Current Implementation**: Flow mode with graceful fallback to Crew mode on errors or complex queries."""

    def _explain_complex_task_delegation(self) -> str:
        """Explain how complex tasks would be delegated"""
        return """## Complex Task Delegation Example

**Task**: "Analyze the performance of my Python script and suggest optimizations"

**Delegation Workflow**:

1. **Terminal Commander** receives request and breaks it down:
   - Need to read the Python script
   - Need to analyze performance characteristics  
   - Need to identify optimization opportunities
   - Need to provide actionable recommendations

2. **Step 1 - File Analysis**:
   - Delegate to **FileNavigator**: "Find Python files in current directory"
   - Delegate to **FileNavigator**: "Read the contents of [script.py]"

3. **Step 2 - Code Analysis**:
   - Delegate to **CodeExecutor**: "Analyze this Python code for performance issues"
   - Delegate to **CodeExecutor**: "Profile the script execution if safe to run"

4. **Step 3 - Research**:
   - Delegate to **WebResearcher**: "Find optimization techniques for [identified issues]"

5. **Step 4 - Synthesis**:
   - **Terminal Commander** combines all results
   - Provides comprehensive analysis with specific recommendations
   - Includes code examples and performance improvement estimates

This demonstrates the system's ability to orchestrate multiple specialists for complex analytical tasks."""

    def _explain_system_architecture(self) -> str:
        """Provide general system architecture overview"""
        return """## Terminal Assistant Architecture

**Core Components**:
- **TerminalAssistantFlow**: Orchestrates command processing and routing
- **Specialized Agents**: FileNavigator, CodeExecutor, WebResearcher, PerformanceMonitor
- **CrewFactory**: Creates specialized crews for different task types
- **StateTracker**: Maintains session state and context
- **DelegateTool**: Enables inter-agent communication

**Agent Specializations**:
- **FileNavigator**: File system operations, directory navigation
- **CodeExecutor**: Safe code execution, debugging, analysis
- **WebResearcher**: Information gathering, documentation lookup
- **PerformanceMonitor**: System monitoring, profiling

**Key Features**:
- Intelligent command classification and routing
- Multi-agent collaboration for complex tasks
- State persistence across commands
- Graceful error handling and fallback mechanisms
- Safety-first approach to code execution"""

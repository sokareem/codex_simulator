from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from crewai import Flow, or_
from crewai.flow.flow import listen, start
from ..flows.crew_factories import CrewFactory
from ..flows.state_manager import StateTracker

class TerminalAssistantFlow(Flow):
    """Flow for handling terminal assistant operations with intelligent routing."""
    
    def __init__(self, llm, state_manager: StateTracker):
        """Initialize the terminal assistant flow.
        
        Args:
            llm: Language model instance for agent creation
            state_manager: State tracker for maintaining context
        """
        super().__init__()
        self.llm = llm
        self.state_manager = state_manager
        self.crew_factory = CrewFactory(llm=llm)
        
    @start()
    def parse_command(self) -> str:
        """Parse and classify the incoming command."""
        command = self.state["command"]
        self.state["parsed_command"] = command
        self.state["timestamp"] = datetime.now().isoformat()
        
        # Classify command intent
        if any(keyword in command.lower() for keyword in ["help", "commands", "what can you do"]):
            return "simple_query"
        elif any(keyword in command.lower() for keyword in ["list", "ls", "files", "directory"]):
            return "file_operation"
        elif any(keyword in command.lower() for keyword in ["run", "execute", "python", "script"]):
            return "code_execution"
        elif any(keyword in command.lower() for keyword in ["search", "find", "weather", "internet"]):
            return "web_research"
        elif any(keyword in command.lower() for keyword in ["explain", "how", "what", "where", "why"]):
            return "system_introspection"
        else:
            return "general_task"
    
    @listen(or_("simple_query", "system_introspection"))
    def handle_simple_query(self) -> str:
        """Handle simple queries and system introspection."""
        command = self.state["parsed_command"]
        
        if "help" in command.lower() or "commands" in command.lower():
            self.state["result"] = self._get_help_message()
        elif "what can you do" in command.lower() or "capable" in command.lower():
            self.state["result"] = self._get_capabilities_message()
        elif "where am i" in command.lower() or "location" in command.lower():
            self.state["result"] = f"You are currently located in: {self.state_manager.current_directory}"
        elif any(keyword in command.lower() for keyword in ["explain", "how", "what", "why"]):
            self.state["result"] = self._handle_explanation_request(command)
        else:
            self.state["result"] = f"I understand you want to: {command}\n\nI can help with file operations, code execution, and web searches. Could you break this down into more specific tasks?"
        
        return "format_response"
    
    @listen("file_operation")
    def delegate_to_file_crew(self) -> str:
        """Delegate file operations to specialized crew."""
        try:
            crew = self.crew_factory.create_file_crew(self.state)
            result = crew.kickoff()
            self.state["result"] = str(result)
            
            # Update working directory if changed
            if "cd " in self.state["command"].lower():
                self.state_manager.update_directory_from_command(self.state["command"])
            
        except Exception as e:
            self.state["result"] = f"File operation failed: {str(e)}"
        
        return "format_response"
    
    @listen("code_execution")
    def delegate_to_code_crew(self) -> str:
        """Delegate code execution to specialized crew."""
        try:
            crew = self.crew_factory.create_code_crew(self.state)
            result = crew.kickoff()
            self.state["result"] = str(result)
        except Exception as e:
            self.state["result"] = f"Code execution failed: {str(e)}"
        
        return "format_response"
    
    @listen("web_research")
    def delegate_to_research_crew(self) -> str:
        """Delegate web research to specialized crew."""
        try:
            crew = self.crew_factory.create_research_crew(self.state)
            result = crew.kickoff()
            self.state["result"] = str(result)
        except Exception as e:
            self.state["result"] = f"Web research failed: {str(e)}"
        
        return "format_response"
    
    @listen("general_task")
    def delegate_to_general_crew(self) -> str:
        """Delegate general tasks to comprehensive crew."""
        try:
            crew = self.crew_factory.create_terminal_crew(self.state)
            result = crew.kickoff()
            self.state["result"] = str(result)
        except Exception as e:
            self.state["result"] = f"Task execution failed: {str(e)}"
        
        return "format_response"
    
    @listen(or_("format_response"))
    def format_response(self) -> str:
        """Format the final response."""
        result = self.state.get("result", "No result available")
        self.state["formatted_result"] = result
        return "complete"
    
    def _get_help_message(self) -> str:
        """Get help message with available commands."""
        return """
# Available Commands in Claude Terminal Assistant
## File Navigation & System Info Commands
- `ls [directory]` - List files and directories
- `pwd` - Show current directory
- `cd [directory]` - Change current working directory
- `find [pattern]` - Search for files by pattern
- `cat [file]` - Display file contents
- `head [file]` - Show first few lines of a file
- `tail [file]` - Show last few lines of a file
- `grep [pattern] [file]` - Search for pattern in file
- `wc [file]` - Count lines, words, and characters in file
- `stat [file/directory]` - Display file or file system status
- `file [file]` - Determine file type
- `df -h` - Show disk space usage (human-readable)
- `du -sh [path]` - Show total size of a directory (human-readable)
- `ps aux` - List running processes
- `top` - Show real-time process summary
- `uname -a` - Show system and kernel information
- `whoami` - Show current user
- `history` - Display command history
- `which [command]` - Show full path to an executable
- `tar -czvf [archive.tar.gz] [files]` - Create a compressed tarball
- `zip [archive.zip] [files]` - Create a ZIP archive
- `unzip [archive.zip]` - Extract a ZIP archive
## Code Execution Commands
- `python [file.py]` - Run Python file
- `python3 [file.py]` - Run Python file with Python 3
- `pip install [package]` - Install Python package
- `pip3 install [package]` - Install Python package with pip3
- `node [file.js]` - Execute JavaScript file
- `npm [command]` - Run npm command
- `yarn [command]` - Run yarn command
- `echo [text]` - Print text to output
- `mkdir [directory]` - Create new directory
- `touch [file]` - Create new empty file
## Special Commands
- `search [query]` - Search the web for information
- `exit` or `quit` - Exit the terminal assistant
- `help` or `commands` - Show this list of commands
## Natural Language Interface
You can also use natural language queries like:
- "Show files in current directory"
- "What's in this directory?"
- "Read the file README.md"
- "Create a new Python file that prints Hello World"
- "Find files containing the word 'test'"
"""
    
    def _get_capabilities_message(self) -> str:
        """Get capabilities description."""
        return """As the Terminal Command Orchestrator and AI Assistant, I am designed to understand your terminal commands and queries, then delegate them to specialized AI agents to get the job done. I act as a central coordinator, ensuring your requests are handled safely and efficiently.

Here's a breakdown of what I'm capable of, through my specialist agents:

*   **File System Operations:** I can delegate tasks to the **FileNavigator** to help you navigate your file system, list directory contents, read files, and manage files safely.
*   **Code Execution:** I can delegate tasks to the **CodeExecutor** to run code snippets or scripts in various programming languages securely.
*   **Web Research:** I can delegate tasks to the **WebResearcher** to perform web searches and retrieve information from the internet.

My primary goal is to assist you in managing your terminal environment, executing commands, and finding information, all while maintaining awareness of your current working directory and ensuring safe operations."""
    
    def _handle_explanation_request(self, command: str) -> str:
        """Handle explanation requests about the system."""
        if "delegation" in command.lower() or "agent" in command.lower():
            return """## Agent Delegation Mechanism

The terminal assistant uses a hierarchical delegation system with the following logic:

**1. Intent Classification**: Commands are analyzed for keywords and patterns to determine which specialist can handle them.

**2. Prioritization Logic**: When multiple specialists could handle a task:
   - **File operations** (ls, cd, find) → FileNavigator
   - **Code execution** (python, scripts) → CodeExecutor
   - **Web searches** (search, weather) → WebResearcher

**3. Delegation Process**:
   - Terminal Commander analyzes the request
   - Routes to appropriate specialist
   - Receives results and synthesizes response

**4. Multi-Agent Coordination**: For complex tasks requiring multiple specialists, the Terminal Commander orchestrates sequential delegation and combines results.

**5. Fallback Mechanism**: If delegation fails, the system falls back to crew-only mode or provides helpful guidance."""
        
        elif "flow" in command.lower() or "architecture" in command.lower():
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
        
        else:
            return f"I understand you want to: {command}\n\nI can help with file operations, code execution, and web searches. Could you break this down into more specific tasks?"

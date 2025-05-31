import sys
import pathlib
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Add error handling for CrewAI imports
try:
    from crewai import Agent, Crew, Process, Task, Knowledge
    from crewai.project import CrewBase, agent, crew, task
    # Try to import Flow components, but handle gracefully if not available
    try:
        from crewai.flow.flow import listen, or_
        FLOW_AVAILABLE = True
    except ImportError:
        FLOW_AVAILABLE = False
        print("⚠️ CrewAI Flow not available - using crew-only mode")
except ImportError as e:
    print(f"❌ CrewAI import error: {e}")
    print("Please install CrewAI with: pip install 'crewai[tools]>=0.86.0,<1.0.0'")
    sys.exit(1)

# Add error handling for optional imports
try:
    from crewai.agents.agent_builder.base_agent import BaseAgent
except ImportError:
    BaseAgent = None

try:
    from langchain.schema.messages import SystemMessage
except ImportError:
    SystemMessage = None

try:
    import dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False
    print("⚠️ python-dotenv not available")

# Get the absolute path to the project root directory
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()

# Load environment variables from the project's .env file
if dotenv_available:
    dotenv.load_dotenv(PROJECT_ROOT / ".env")

# Import the custom LLM with error handling
try:
    from .llms.custom_gemini_llm import CustomGeminiLLM
except ImportError:
    print("⚠️ Custom Gemini LLM not available")
    CustomGeminiLLM = None

# Tool imports with error handling
try:
    from codex_simulator.tools.safe_shell_tool import SafeShellTool
    from codex_simulator.tools.safe_directory_tool import SafeDirectoryTool
    from codex_simulator.tools.safe_file_read_tool import SafeFileReadTool
    from codex_simulator.tools.safe_file_write_tool import SafeFileWriteTool
except ImportError as e:
    print(f"❌ Core tool import error: {e}")
    sys.exit(1)

# Optional tool imports
try:
    from codex_simulator.tools.serp_api_tool import SerpAPITool
    from codex_simulator.tools.website_tool import WebsiteTool
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    WEB_TOOLS_AVAILABLE = False
    SerpAPITool = None
    WebsiteTool = None

try:
    from codex_simulator.utils.delegation_fix import get_delegation_handler
    from codex_simulator.utils.file_operations import FileOperationsManager
    from codex_simulator.utils.tool_adapter import patch_tool_methods
    from codex_simulator.utils.simple_knowledge import SimpleKnowledge
    from codex_simulator.tools.fs_cache_tool import FSCacheTool
    from codex_simulator.tools.execution_profiler_tool import ExecutionProfilerTool
    from codex_simulator.tools.delegate_tool import DelegateTool
    from codex_simulator.tools.pdf_reader_tool import PDFReaderTool
except ImportError as e:
    print(f"⚠️ Optional component import warning: {e}")

# Import new tools with error handling
try:
    from .tools.new_tools import (
        EnvironmentVariableTool, StaticCodeAnalysisTool, GitManagementTool,
        NetworkDiagnosticTool, PlottingTool, SystemMonitoringTool
    )
    NEW_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ New tools not available: {e}")
    NEW_TOOLS_AVAILABLE = False

# MCP imports with error handling
try:
    from .mcp import MCPClient, MCPToolWrapper, MCPConnectionConfig, create_mcp_client, wrap_tools_with_mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP integration not available")

# Class for structured state tracking
class StateTracker:
    """Tracks state across agent interactions"""
    def __init__(self, initial_cwd: str = os.getcwd()):
        self.cwd = initial_cwd
        self.command_history = []
        self.context_data = {}
    
    def update_cwd(self, new_cwd: str) -> None:
        """Update current working directory if it exists"""
        if os.path.isdir(new_cwd):
            self.cwd = os.path.abspath(new_cwd)
            return True
        return False
    
    def add_command(self, command: str) -> None:
        """Add a command to the history"""
        self.command_history.append(command)
    
    def update_context(self, key: str, value: Any) -> None:
        """Update a context value"""
        self.context_data[key] = value
    
    def extract_cwd_from_response(self, response: str) -> Optional[str]:
        """Extract updated CWD from a response if present"""
        # Look for patterns like "Changed directory to: /path/to/dir"
        patterns = [
            r"Changed directory to: ([^\n]+)",
            r"Current working directory: ([^\n]+)",
            r"CWD: ([^\n]+)",
            r"Current directory: ([^\n]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                potential_cwd = match.group(1).strip()
                if os.path.isdir(potential_cwd):
                    return potential_cwd
        
        return None

def remove_competing_delegation_tools(agent):
    if hasattr(agent, 'tools'):
        # More comprehensive list of potential default/competing delegation tool names
        competing_tool_names = [
            'delegate',  # Original
            'ask_question',  # Original
            'Delegate work to coworker', # Seen in logs
            'Ask question to coworker',   # Seen in logs
            'Delegate Task to Coworker' # Added variation
        ]
        # Normalize to lower case for comparison
        competing_tool_names_lower = [name.lower() for name in competing_tool_names]
        
        original_tool_count = len(agent.tools)
        agent.tools = [
            t for t in agent.tools 
            if t.name.lower() not in competing_tool_names_lower
        ]
        
        if len(agent.tools) < original_tool_count:
            agent_name = agent.role if hasattr(agent, 'role') else 'Unknown Agent'
            print(f"Removed competing delegation tools from agent {agent_name}. Remaining tools: {[t.name for t in agent.tools]}")
        # Debug print to see all tools after potential cleanup
        # print(f"Agent tools after cleanup for {agent.role if hasattr(agent, 'role') else 'Unknown Agent'}: {[t.name for t in agent.tools]}")

@CrewBase
class CodexSimulator:
    """Main class for the CodexSimulator terminal assistant with Flow orchestration support."""
    agents_config = 'config/agents.yaml'  # Added: Path relative to this file
    tasks_config = 'config/tasks.yaml'    # Added: Path relative to this file
    
    def __init__(self, use_mcp: bool = False, mcp_server_url: str = "http://localhost:8000"):
        """Initialize CodexSimulator with optional MCP support.
        
        Args:
            use_mcp: Whether to enable MCP integration
            mcp_server_url: URL of the MCP server
        """
        self.use_mcp = use_mcp
        self.mcp_server_url = mcp_server_url
        self.mcp_client = None
        self._mcp_initialized = False  # Initialize the flag
        
        # Initialize state tracker and LLM
        self.state_tracker = StateTracker()
        self.llm = self._create_llm()
        
        # Flow control
        self.flow_enabled = True 
        
        # Removed: asyncio.create_task(self._initialize_mcp())
        # MCP initialization will be handled by initialize_mcp_if_needed
    
    async def _initialize_mcp(self):
        """Initialize MCP client asynchronously."""
        # This method is kept for now, but initialize_mcp_if_needed is the primary one.
        # If this method were to be used directly, it MUST set _mcp_initialized.
        try:
            from .mcp import create_mcp_client # Ensure import is correct
            self.mcp_client = await create_mcp_client(
                server_url=self.mcp_server_url,
                agent_id="codex_simulator_main",
                timeout=30
            )
            print(f"✅ MCP client connected to {self.mcp_server_url}")
            self._mcp_initialized = True # Set flag on success
        except Exception as e:
            print(f"⚠️ Failed to connect to MCP server: {e}")
            print("Falling back to direct tool execution")
            self.use_mcp = False
            self._mcp_initialized = True # Set flag on fallback
    
    async def initialize_mcp_if_needed(self):
        """Initialize MCP client if needed and not already initialized"""
        if self.use_mcp and not self._mcp_initialized: # This read is now safe
            try:
                from .mcp import create_mcp_client # Ensure import is correct
                self.mcp_client = await create_mcp_client(
                    server_url=self.mcp_server_url,
                    agent_id="codex_simulator_main",
                    timeout=30
                )
                self._mcp_initialized = True # Set flag on success
                print(f"✅ MCP client connected to {self.mcp_server_url}")
            except Exception as e:
                print(f"⚠️ Failed to connect to MCP server: {e}")
                print("Falling back to direct tool execution")
                self.use_mcp = False
                self._mcp_initialized = True  # Set flag on failure/fallback to avoid retries
    
    async def cleanup_mcp(self):
        """Cleanup MCP connection."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
    
    def _create_llm(self):
        """Create and configure the LLM."""
        try:
            model_env_name = os.environ['MODEL'] 
            gemini_api_key_env = os.environ['GEMINI_API_KEY']
        except KeyError as e:
            print(f"Error: Environment variable {e} not set. Please ensure MODEL and GEMINI_API_KEY are in your .env file.")
            raise ValueError(f"Missing environment variable: {e}")

        # Instantiate the custom LLM wrapper
        return CustomGeminiLLM(
            model=model_env_name,
            google_api_key=gemini_api_key_env,
            temperature=0.7 
        )

    async def terminal_assistant(self, command: str) -> str:
        """Enhanced terminal assistant with flow support"""
        # Initialize MCP if needed
        await self.initialize_mcp_if_needed()
        
        if self.flow_enabled:
            return self._run_with_flow(command)
        else:
            return self._run_with_crew_only(command)  # Fallback to current implementation

    def _run_with_flow(self, command: str) -> str:
        """Run command through flow orchestration"""
        try:
            from .flows.terminal_flow import TerminalAssistantFlow
            
            if not self.terminal_flow:
                self.terminal_flow = TerminalAssistantFlow()
            
            # Set command through proper Flow mechanism
            self.terminal_flow._input_command = command
            
            print(f"Starting flow with command: {command}")
            
            # Kickoff Flow properly
            flow_result = self.terminal_flow.kickoff()
            
            # Extract response from flow result
            if isinstance(flow_result, dict):
                if flow_result.get('clarification_needed'):
                    # Ensure clarification requests are passed clearly
                    return f"CLARIFICATION_REQUEST:{flow_result.get('response', 'Please provide more details.')}"
                
                response = flow_result.get('response', 'Flow execution completed without a specific response.')
                # Update state based on command execution
                self._update_state_from_flow_result(flow_result, command)
                return response
            elif isinstance(flow_result, str):
                # Handle cases where flow might return a simple string
                self._update_state_from_flow_result({'response': flow_result}, command)
                return flow_result
            else:
                # Fallback for unexpected flow_result types
                unknown_response = f"Flow execution resulted in an unexpected data type: {type(flow_result)}. Result: {str(flow_result)}"
                self._update_state_from_flow_result({'response': unknown_response}, command)
                return unknown_response
        except Exception as e:
            # Graceful fallback to crew-only mode
            error_message = f"Flow execution failed for command '{command}'. Error: {str(e)}. Falling back to crew-only mode."
            print(error_message)
            # Log this specific error to CLAUDE.md before falling back
            self._update_claude_md(command, f"FLOW_ERROR: {error_message}\nFALLING_BACK_TO_CREW_MODE")
            return self._run_with_crew_only(command)
    
    def _update_state_from_flow_result(self, flow_result: Dict, command: str):
        """Update system state based on flow execution results"""
        # Update command history
        self._state.add_command(command)
        
        # Update CLAUDE.md with results
        if 'response' in flow_result:
            self._update_claude_md(command, flow_result['response'])
        
        # Extract any directory changes from the response
        if 'response' in flow_result:
            new_cwd = self._state.extract_cwd_from_response(flow_result['response'])
            if new_cwd:
                self.cwd = new_cwd
            # Ensure CLAUDE.md is updated even if CWD didn't change in this specific response
            elif 'response' in flow_result: # Ensure there's a response to log
                self._update_claude_md(command, flow_result['response'])

    def _create_knowledge_sources(self):
        """Create knowledge sources for agents - return None to avoid validation issues"""
        # Return None instead of SimpleKnowledge to avoid CrewAI validation errors
        # CrewAI expects specific Knowledge types, not custom classes
        return None

    def _assess_command_complexity(self, command: str) -> int:
        """Assess command complexity on a scale of 1-10"""
        command_lower = command.lower().strip()
        complexity = 1
        
        # Multiple operations indicator
        if any(sep in command for sep in [';', '&&', '||', '|']):
            complexity += 3
        
        # File system operations
        if any(op in command_lower for op in ['find', 'grep', 'chmod', 'chown']):
            complexity += 2
        
        # Code execution
        if any(lang in command_lower for lang in ['python', 'node', 'npm', 'pip']):
            complexity += 2
        
        # Web operations
        if any(web in command_lower for web in ['search', 'curl', 'wget']):
            complexity += 1
        
        # Natural language complexity
        if len(command.split()) > 5:
            complexity += 1
        
        # Context-dependent operations
        if any(ctx in command_lower for ctx in ['if', 'while', 'for', 'then']):
            complexity += 2
        
        return min(complexity, 10)

    def _run_with_crew_only(self, command: str) -> str:
        """Original crew-only implementation as fallback"""
        # Record command in history
        self._state.add_command(command)
        # Ensure CLAUDE.md exists for shared state
        self._ensure_claude_md_exists()
        # Load context
        user_context = self._load_user_context()
        claude_context = self._load_claude_context()
        # Enhanced check for help and commands request directly
        help_keywords = ["help", "command", "available", "what can you do", "list all", "show me"]
        command_lower = command.strip().lower() # Corrected to lower()
        is_help_request = any(kw in command_lower for kw in help_keywords) and \
                          ("command" in command_lower or "help" in command_lower or "available" in command_lower or "what can you do" in command_lower)
        if command_lower in ["help", "commands", "list commands", "show commands", "available commands", 
                             "what commands are available", "what can you do", "list all available commands i can run"] or is_help_request:
            result = self._get_available_commands()
            self._update_claude_md(command, result)
            return result
        # Handle directory changes
        if command.strip().startswith("cd "): # Corrected to startswith()
            return self._handle_cd_command(command)
        # Handle basic pwd/directory query
        if command_lower in ["pwd", "where am i", "what directory am i in", "current directory"]:
            result = f"Current directory: {self.cwd}"
            self._update_claude_md(command, result)
            return result
        # Process normal commands through the crew
        try:
            # Create and run crew
            terminal_crew = self._create_terminal_crew(command, user_context, claude_context)
            inputs = {
                'user_command': command,
                'cwd': self.cwd,
                'user_context': user_context,
                'claude_context': claude_context
            }
            crew_result = terminal_crew.kickoff(inputs=inputs)
            # Handle CrewOutput object vs string - extract string content
            if hasattr(crew_result, 'raw_output'):
                result = str(crew_result.raw_output)
            elif hasattr(crew_result, 'result'):
                result = str(crew_result.result)
            elif hasattr(crew_result, 'output'):
                result = str(crew_result.output)
            else:
                # Fall back to string representation
                result = str(crew_result)
            # Check if result contains CWD update
            new_cwd = self._state.extract_cwd_from_response(result)
            if new_cwd:
                self.cwd = new_cwd
            # Update shared memory
            self._update_claude_md(command, result)
            return result
        except Exception as e:
            error_result = f"Error processing command '{command}': {str(e)}. Please check the command syntax or try rephrasing."
            self._update_claude_md(command, error_result)
            return error_result

    def _handle_cd_command(self, command: str) -> str:
        """Handle directory changes explicitly"""
        directory = command.strip()[3:].strip()
        new_dir = os.path.abspath(os.path.join(self.cwd, directory))
        if os.path.isdir(new_dir):
            self.cwd = new_dir
            result = f"Changed directory to: {self.cwd}"
            self._update_claude_md(command, result)
            return result
        else:
            result = f"Directory not found: {directory}"
            self._update_claude_md(command, result)
            return result

    def _load_user_context(self) -> str:
        """Load user preferences context"""
        user_context = "No user context available. User preferences can be set in 'knowledge/user_preference.txt'."
        try:
            user_pref_path = PROJECT_ROOT / "knowledge" / "user_preference.txt"
            if user_pref_path.exists():
                with open(user_pref_path, "r") as f:
                    user_context_content = f.read().strip()
                    if user_context_content:
                        user_context = user_context_content
        except Exception as e:
            print(f"Warning: Could not load user preferences: {e}")
        return user_context

    def _load_claude_context(self) -> str:
        """Load CLAUDE.md context"""
        claude_context = ""
        claude_md_path = os.path.join(self.cwd, "CLAUDE.md") # Ensure CWD is used
        if os.path.exists(claude_md_path):
            try:
                with open(claude_md_path, "r", encoding="utf-8") as f:
                    claude_context = f.read()
            except Exception as e:
                print(f"Warning: Could not read CLAUDE.md: {e}")
        return claude_context

    def _ensure_claude_md_exists(self):
        """Ensure that CLAUDE.md file exists in the current directory."""
        claude_md_path = os.path.join(self.cwd, "CLAUDE.md") # Ensure CWD is used
        if not os.path.exists(claude_md_path):
            # Create initial CLAUDE.md with enhanced structure
            initial_content = (
                f"# Claude Memory File\n\n"
                f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Initial Working Directory: {self.cwd}\n\n"
                f"## Context\n\n"
                f"This file serves as shared memory for the Claude Terminal Assistant.\n"
                f"It tracks command history and maintains context between sessions.\n"
                f"User preferences can be configured in 'knowledge/user_preference.txt'.\n\n"
                f"## Directory Information\n\n"
                f"Current Working Directory: {self.cwd}\n\n"
                f"## Command History\n\n"
            )
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write(initial_content)

    def _update_claude_md(self, command: str, result: str):
        """Update the CLAUDE.md file with enhanced formatting"""
        claude_md_path = os.path.join(self.cwd, "CLAUDE.md") # Ensure CWD is used
        # Read existing content
        existing_content = ""
        try:
            if os.path.exists(claude_md_path):
                with open(claude_md_path, "r", encoding="utf-8") as f:
                    existing_content = f.read()
        except Exception as e:
            print(f"Warning: Could not read CLAUDE.md: {e}")
        # Update command history with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        command_entry = (
            f"### {timestamp}\n\n"
            f"**Command:** `{command}`\n\n"
            f"**Working Directory:** `{self.cwd}`\n\n"
            f"**Result:**\n\n```\n{result}\n```\n\n"
        )
        # Find the command history section or add it
        if "## Command History" in existing_content:
            parts = existing_content.split("## Command History")
            new_content = parts[0] + "## Command History\n\n" + command_entry + parts[1].split("###", 1)[-1] if len(parts) > 1 and "###" in parts[1] else ""
        else:
            new_content = existing_content + "\n## Command History\n\n" + command_entry
        # Write the updated content
        try:
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"Warning: Could not write to CLAUDE.md: {e}")

    def _get_available_commands(self) -> str:
        """Return information about all available commands in the terminal assistant."""
        commands_info = """
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

## Code Execution & Analysis Commands
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
- `analyze_code [file.py]` - Perform static security analysis on a Python file.

## PDF Document Commands
- `read_pdf [path/to/file.pdf]` - Read all text from a PDF.
- `chunk_pdf [path/to/file.pdf] [chunk_size] [overlap]` - Break PDF into text chunks.

## Configuration Management Commands
- `env list` - List all environment variables.
- `env get [VAR_NAME]` - Get the value of an environment variable.
- `env set [VAR_NAME]=[VALUE]` - Set an environment variable.
- `env unset [VAR_NAME]` - Unset an environment variable.

## Git Management Commands
- `git status [repo_path]` - Show Git repository status.
- `git clone [remote_url] [local_path]` - Clone a Git repository.
- `git pull [repo_path]` - Pull changes from remote.
- `git push [repo_path]` - Push changes to remote.
- `git commit [repo_path] -m "[message]"` - Commit changes.
- `git branch [repo_path] [branch_name]` - Create or list branches.
- `git checkout [repo_path] [branch_name]` - Switch branches.

## Network Diagnostic Commands
- `ping [host] [count=4]` - Ping a host.
- `traceroute [host]` - Trace route to a host.
- `nslookup [host]` - Perform DNS lookup for a host.

## Data Visualization Commands
- `plot line data="[1,2,3]" title="My Plot" output="plot.png"` - Create a line plot.
- `plot bar data='{"a":1,"b":2}' title="Bar Chart" output="bar.png"` - Create a bar plot.
  (Data can be a JSON string list/dict, or path to a file to be read by an agent)

## System Monitoring Commands
- `monitor cpu` - Get current CPU usage.
- `monitor memory` - Get memory usage statistics.
- `monitor disk [path=/]` - Get disk usage for a path.
- `monitor network` - Get network I/O statistics.
- `monitor processes [sort_by=cpu_percent] [limit=10]` - List running processes.

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
- "Set environment variable API_KEY to 12345"
- "What's the status of my project in /path/to/repo?"
- "Ping google.com 5 times"
- "Plot sales data from sales.csv as a line graph titled 'Monthly Sales'"
"""
        return commands_info

    def create_report_crew(self) -> Crew:
        """Creates a specialized crew just for report generation, 
        avoiding terminal-specific tasks"""
        researcher_agent = self.researcher()
        reporting_agent = self.reporting_analyst()
        
        # Create research task that doesn't rely on terminal-specific variables
        research_task = Task(
            description=f"Conduct thorough research on the topic: '{{topic}}'.\n"
                       f"Identify key developments, current trends, significant factual information, "
                       f"and notable opinions or analyses.\n"
                       f"Ensure information is relevant to the current year: {{current_year}}.",
            expected_output="A concise, well-organized list of 10-15 bullet points summarizing the most relevant findings",
            agent=researcher_agent
        )
        
        # Create reporting task that doesn't rely on terminal-specific variables
        reporting_task = Task(
            description=f"Based on the research findings about '{{topic}}', "
                       f"create a comprehensive and well-structured report.\n"
                       f"Expand each key finding into a detailed section, providing supporting information, "
                       f"analysis, and examples where appropriate.",
            expected_output="A fully fledged report in clean markdown format",
            agent=reporting_agent,
            output_file='report.md'
        )
        
        return Crew(
            agents=[researcher_agent, reporting_agent],
            tasks=[research_task, reporting_task],
            process=Process.sequential,
            verbose=True
        )

# In the main function or startup code
try:
    # Import tools upfront to verify they're available
    from codex_simulator.tools import SafeDirectoryTool
    # Continue with application startup
except ImportError as e:
    print(f"❌ Error loading required tool: {str(e)}")
    print("Please ensure all dependencies are installed by running:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Try importing the tools and handle any errors gracefully
def safe_import_tool(tool_path, tool_name):
    """Safely import a tool and return None if it fails"""
    try:
        module_path, class_name = tool_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        tool_class = getattr(module, class_name)
        return tool_class()
    except Exception as e:
        print(f"⚠️ Failed to import {tool_name}: {e}")
        return None

# In the main function or startup code
try:
    # Test import and instantiation
    from codex_simulator.tools.safe_directory_tool import SafeDirectoryTool
    test_tool = SafeDirectoryTool()
    print(f"✅ SafeDirectoryTool imported and instantiated successfully")
except Exception as e:
    print(f"❌ Error with SafeDirectoryTool: {str(e)}")
    print("Please check the tool implementation")
    import traceback
    traceback.print_exc()
    sys.exit(1)
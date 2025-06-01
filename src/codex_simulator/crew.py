import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from crewai import Agent, Task, Crew, Process, Flow
from crewai.flow.flow import listen, or_

from crewai import Agent, Crew, Process, Task, Knowledge
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain.schema.messages import SystemMessage
from typing import Dict, List, Any, Optional, Union
import os
import json
from datetime import datetime
import dotenv
import pathlib
import re

# Get the absolute path to the project root directory
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()

# Load environment variables from the project's .env file
dotenv.load_dotenv(PROJECT_ROOT / ".env")

# Import the custom LLM
from .llms.custom_gemini_llm import CustomGeminiLLM

# Explicitly import the tools we need
from codex_simulator.tools.safe_shell_tool import SafeShellTool
from codex_simulator.tools.safe_directory_tool import SafeDirectoryTool
from codex_simulator.tools.safe_file_read_tool import SafeFileReadTool
from codex_simulator.tools.safe_file_write_tool import SafeFileWriteTool
from codex_simulator.tools.serp_api_tool import SerpAPITool
from codex_simulator.tools.website_tool import WebsiteTool
from codex_simulator.utils.delegation_fix import get_delegation_handler
from codex_simulator.utils.file_operations import FileOperationsManager
from codex_simulator.utils.tool_adapter import patch_tool_methods
from codex_simulator.utils.simple_knowledge import SimpleKnowledge  # Add this import
from codex_simulator.tools.fs_cache_tool import FSCacheTool    # new import
from codex_simulator.tools.execution_profiler_tool import ExecutionProfilerTool  # new import
from codex_simulator.tools.delegate_tool import DelegateTool  # Import our new delegate tool
from codex_simulator.tools.delegate_tool import MCPDelegateTool  # Add this import
from codex_simulator.tools.pdf_reader_tool import PDFReaderTool # Import PDFReaderTool

# Add MCP imports
from .mcp import MCPClient, MCPToolWrapper, MCPConnectionConfig, create_mcp_client, wrap_tools_with_mcp

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
            'Ask question to coworker'   # Seen in logs
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
            from .mcp.client import create_mcp_client # Ensure import is correct
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

    async def initialize_mcp_if_needed(self):
        """Initialize MCP client if needed and not already initialized"""
        if self.use_mcp and not self._mcp_initialized:
            try:
                self.mcp_client = await create_mcp_client(
                    server_url=self.mcp_server_url,
                    agent_id="codex_simulator_main",
                    timeout=30
                )
                self._mcp_initialized = True
                print(f"✅ MCP client connected to {self.mcp_server_url}")
            except Exception as e:
                print(f"⚠️ Failed to connect to MCP server: {e}")
                print("Falling back to direct tool execution")
                self.use_mcp = False
                self._mcp_initialized = True  # Mark as "initialized" to avoid retries
    
    async def cleanup_mcp(self):
        """Cleanup MCP client connection"""
        if self.mcp_client:
            try:
                await self.mcp_client.disconnect()
                print("🔌 MCP client disconnected")
            except Exception as e:
                print(f"Warning: Error disconnecting MCP client: {e}")
    
    def _create_tools(self, agent_type: str = "general") -> List[Any]:
        """Create tools for agents, optionally wrapping with MCP"""
        # Create base tools
        tools = []
        
        if agent_type == "file":
            tools = [
                SafeDirectoryTool(),
                SafeFileReadTool(),
                SafeFileWriteTool(),
                FSCacheTool()
            ]
        elif agent_type == "code":
            tools = [
                SafeShellTool(),
                ExecutionProfilerTool()
            ]
        elif agent_type == "web":
            tools = [
                SerpAPITool(),
                WebsiteTool()
            ]
        elif agent_type == "pdf": # New agent type for PDF
            tools = [PDFReaderTool()]
        elif agent_type == "terminal":
            # Terminal commander gets delegation tool
            tools = [DelegateTool(agents_dict=self._get_agents_dict())]
        
        # Wrap tools with MCP if enabled
        if self.use_mcp and self.mcp_client:
            tool_names = [tool.name for tool in tools]
            mcp_tools = wrap_tools_with_mcp(tool_names, self.mcp_client)
            return mcp_tools
        
        return tools
    
    def _get_agents_dict(self) -> Dict[str, Any]:
        """Get dictionary of available agents for delegation"""
        # This will be populated with actual agent instances
        # For now, return empty dict to avoid circular dependencies
        # Update this when agents are fully defined
        return {
            "FileNavigator": self.file_navigator(),
            "CodeExecutor": self.code_executor(),
            "WebResearcher": self.web_researcher(),
            "PDFDocumentAnalyst": self.pdf_document_analyst() # Add PDF agent
        }
    
    def _create_file_navigator_agent(self) -> Agent:
        """Create the File Navigator agent"""
        return Agent(
            role='Expert File System Navigator and Operations Specialist',
            goal='Navigate file systems efficiently and perform file operations safely with comprehensive error handling and user guidance.',
            backstory="""You are an expert file system navigator with deep knowledge of Unix/Linux and 
            Windows file systems. You excel at directory navigation, file operations, and providing 
            clear guidance to users about file system structure and operations.""",
            tools=self._create_tools("file"),
            verbose=True,
            llm=self._get_llm()
        )
    
    def _create_code_executor_agent(self) -> Agent:
        """Create the Code Executor agent"""
        return Agent(
            role='Secure Code and Command Execution Specialist',
            goal='Execute code and commands safely in controlled environments with comprehensive security measures and performance monitoring.',
            backstory="""You are a security-conscious code execution specialist with expertise in 
            sandboxing, performance monitoring, and safe command execution. You prioritize security 
            while enabling powerful development workflows.""",
            tools=self._create_tools("code"),
            verbose=True,
            llm=self._get_llm()
        )
    
    def _create_web_researcher_agent(self) -> Agent:
        """Create the Web Researcher agent"""
        return Agent(
            role='Expert Web Research and Information Gathering Specialist',
            goal='Conduct thorough web research and gather accurate, relevant information from online sources.',
            backstory="""You are an expert researcher with exceptional skills in finding, evaluating, 
            and synthesizing information from web sources. You excel at using search engines effectively 
            and extracting valuable insights from websites.""",
            tools=self._create_tools("web"),
            verbose=True,
            llm=self._get_llm()
        )

    def _create_pdf_document_analyst_agent(self) -> Agent:
        """Create the PDF Document Analyst agent"""
        return Agent(
            role='Expert PDF Document Analyst',
            goal='Read, analyze, summarize, and extract information from PDF documents. Break down large PDFs into manageable chunks for processing.',
            backstory="""You are a specialist in handling PDF documents. You can meticulously read through PDF content, 
            understand its structure, extract key information, provide summaries, and answer questions based on the document.
            You are also skilled at breaking down lengthy PDF documents into smaller, more digestible chunks for further analysis.""",
            tools=self._create_tools("pdf"),
            verbose=True,
            llm=self._get_llm()
        )
    
    def _create_terminal_commander_agent(self) -> Agent:
        """Create the Terminal Commander agent with MCP-aware delegation"""
        # Update agents dict for delegation
        agents_dict = {
            "FileNavigator": self._create_file_navigator_agent(),
            "CodeExecutor": self._create_code_executor_agent(),
            "WebResearcher": self._create_web_researcher_agent(),
            "PDFDocumentAnalyst": self._create_pdf_document_analyst_agent() # Add PDF agent
        }
        
        # Create delegation tool with MCP support
        if self.use_mcp and self.mcp_client:
            delegation_tool = MCPDelegateTool(
                agents_dict=agents_dict,
                mcp_client=self.mcp_client
            )
        else:
            delegation_tool = DelegateTool(agents_dict=agents_dict)
        
        return Agent(
            role='Terminal Command Orchestrator and AI Assistant',
            goal='Coordinate and delegate tasks to specialist agents while providing intelligent terminal assistance.',
            backstory="""You are an intelligent terminal assistant and command orchestrator. Your role is to 
            understand user requests, break them down into manageable tasks, and delegate to the most appropriate 
            specialist agents. You excel at task decomposition, coordination, and synthesizing results.""",
            tools=[delegation_tool],
            verbose=True,
            llm=self._get_llm()
        )
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Use the state tracker for state variables
    _state: StateTracker = StateTracker()
    
    @property
    def cwd(self) -> str:
        return self._state.cwd
    
    @cwd.setter
    def cwd(self, value: str) -> None:
        self._state.update_cwd(value)
    
    @property
    def command_history(self) -> List[str]:
        return self._state.command_history
    
    # Setup LLM
    def _get_llm(self):
        """Get the LLM instance configured specifically for Google Gemini,
        using the custom google-generativeai SDK wrapper."""
        
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

    # Original agents
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=self._get_llm(),
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            llm=self._get_llm(),
            verbose=True
        )
    
    # Claude Terminal Assistant agents with enhanced tool configuration
    @agent
    def terminal_commander(self) -> Agent:
        """Central orchestrator agent that delegates to specialists.
        As a manager in a hierarchical process, it should not use tools for delegation."""
        
        # This agent, when acting as a hierarchical manager, delegates via natural language.
        # It should not be assigned the DelegateTool or any other delegation tool.
        # The agent_mapping and delegate_tool instantiation are removed from here
        # as this agent instance will not use them if it's a manager.
        return Agent(
            config=self.agents_config['terminal_commander'],
            llm=self._get_llm(),
            tools=[],  # Explicitly no tools by default for the manager
            verbose=True
        )

    @agent
    def file_navigator(self) -> Agent:
        """Specialist agent for file system operations, now with caching."""
        return Agent(
            config=self.agents_config['file_navigator'],
            llm=self._get_llm(),
            tools=[
                SafeDirectoryTool(),
                SafeFileReadTool(),
                SafeFileWriteTool(),
                # Limited shell commands for file inspection
                SafeShellTool(allowed_commands=[
                    "ls", "pwd", "find", "grep", "cat", "head", "tail", "wc", 
                    "du", "df", "stat", "file", "chmod"
                ]),
                FSCacheTool(),               # added cache tool
            ],
            verbose=True
        )

    @agent
    def code_executor(self) -> Agent:
        """Specialist agent for code execution"""
        return Agent(
            config=self.agents_config['code_executor'],
            llm=self._get_llm(),
            tools=[
                SafeShellTool(
                    allowed_commands=[
                        "python", "python3", "pip", "pip3", "node", "npm", "yarn",
                        "echo", "cat", "mkdir", "cp", "touch", "stat", "file",
                        "ls", "test"
                    ]
                ),
                SafeFileReadTool(),
                SafeFileWriteTool()
            ],
            verbose=True
        )

    @agent
    def web_researcher(self) -> Agent:
        """Specialist agent for web research"""
        return Agent(
            config=self.agents_config['web_researcher'],
            llm=self._get_llm(),
            tools=[
                SerpAPITool(),
                WebsiteTool(),
                SafeFileReadTool(),
                SafeFileWriteTool(allowed_files=["CLAUDE.md"])
            ],
            verbose=True
        )

    @agent
    def pdf_document_analyst(self) -> Agent:
        """Specialist agent for PDF document analysis."""
        return Agent(
            config=self.agents_config.get('pdf_document_analyst', { # Provide default config
                'role': 'Expert PDF Document Analyst',
                'goal': 'Read, analyze, summarize, and extract information from PDF documents. Break down large PDFs into manageable chunks for processing.',
                'backstory': """You are a specialist in handling PDF documents. You can meticulously read through PDF content, 
                understand its structure, extract key information, provide summaries, and answer questions based on the document.
                You are also skilled at breaking down lengthy PDF documents into smaller, more digestible chunks for further analysis."""
            }),
            llm=self._get_llm(),
            tools=[PDFReaderTool()], # Directly assign the tool
            verbose=True
        )

    @agent
    def performance_monitor(self) -> Agent:
        """New agent to profile and report execution metrics."""
        return Agent(
            config=self.agents_config['performance_monitor'],
            llm=self._get_llm(),
            tools=[
                ExecutionProfilerTool(),
                SafeShellTool(allowed_commands=[
                    "ps", "top", "df", "du", "free", "uname", "whoami", "which",
                    "lscpu", "lsmem", "iostat", "vmstat"
                ])
            ],
            verbose=False
        )

    # Tasks remain largely unchanged
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def process_command_task(self) -> Task:
        return Task(
            config=self.tasks_config['process_command_task'], # type: ignore[index]
        )

    @task
    def navigate_files_task(self) -> Task:
        return Task(
            config=self.tasks_config['navigate_files_task'], # type: ignore[index]
        )

    @task
    def execute_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['execute_code_task'], # type: ignore[index]
        )

    @task
    def web_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_search_task'], # type: ignore[index]
        )

    @task
    def analyze_pdf_task(self) -> Task:
        """Task for analyzing PDF documents."""
        task_config_key = 'analyze_pdf_task'
        # Get config from YAML. It's expected to be there and define the agent by name.
        task_config = self.tasks_config[task_config_key] 
        
        # CrewBase's @task decorator will resolve the agent name in task_config
        # to an actual agent instance from self.agents.
        # So, we just need to return a Task with this config.
        return Task(config=task_config)

    @crew
    def crew(self) -> Crew:
        """Creates the standard report generation crew"""
        # Consistently use _create_knowledge_sources, which will return None.
        # The actual content from user_preference.txt is loaded via _load_user_context
        # and injected into task descriptions if needed by the standard crew's tasks.
        knowledge = self._create_knowledge_sources()
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            llm=self._get_llm(),  # Use Gemini for the manager LLM as well
            verbose=True,
            knowledge=knowledge, # This will be None
        )

    def _create_terminal_crew(self, command: str, user_context: str, claude_context: str = "") -> Crew:
        """Create a dedicated crew for handling terminal commands with enhanced delegation"""
        # Create the terminal commander agent (this will be the manager)
        terminal_agent = self.terminal_commander()
        
        # Define specialist agents (these will be the workers)
        file_nav_agent = self.file_navigator()
        code_exec_agent = self.code_executor()
        web_research_agent = self.web_researcher()
        pdf_analyst_agent = self.pdf_document_analyst() # Add PDF agent
        
        # Apply tool patches to fix unhashable type errors
        patch_tool_methods(file_nav_agent)
        patch_tool_methods(code_exec_agent)
        patch_tool_methods(web_research_agent)
        patch_tool_methods(pdf_analyst_agent) # Patch PDF agent
        
        # Apply the cleanup to all agents that will be part of this crew
        all_agents_in_this_crew_setup = [terminal_agent, file_nav_agent, code_exec_agent, web_research_agent, pdf_analyst_agent]
        for ag in all_agents_in_this_crew_setup:
            remove_competing_delegation_tools(ag)
        
        # Create explicit agent references dictionary for delegation
        agent_registry = {
            "FileNavigator": file_nav_agent,
            "CodeExecutor": code_exec_agent,
            "WebResearcher": web_research_agent,
            "PDFDocumentAnalyst": pdf_analyst_agent # Add PDF agent to registry
        }
        
        # Add tools to manager - explicitly including our own delegate tool
        delegate_tool = DelegateTool(agents_dict=agent_registry)
        terminal_agent.tools = [delegate_tool]
        
        print(f"Manager agent ('{terminal_agent.role}') tools set with custom delegate tool")
        
        # Create task with comprehensive context
        task_description = (
            f"Process the user's terminal command or query: '{command}'\n\n"
            f"Current working directory: {self.cwd}\n"
            f"User context: {user_context}\n"
            f"Command history: {', '.join(self.command_history[-5:]) if self.command_history else 'None'}\n"
            f"Session context: {claude_context[:1000] + '...' if len(claude_context) > 1000 else claude_context}\n\n"
            f"CRITICAL INSTRUCTION FOR MANAGER (YOU - {terminal_agent.role}): You are a manager. Your role is to understand the task and delegate sub-tasks to your specialist coworkers using the delegation tool.\n"
            f"Available specialists: FileNavigator (file operations), CodeExecutor (code execution), WebResearcher (web searches), PDFDocumentAnalyst (PDF analysis).\n"
            f"After receiving results from coworkers, synthesize them into a final answer for the user.\n"
            f"Provide a clear and helpful final response to the user's query, reflecting the action taken or delegated. "
            f"If the command involved a directory change, make sure to include the new directory path in your final response."
        )
        
        task = Task(
            description=task_description,
            agent=terminal_agent,
            expected_output=(
                "A clear and helpful response to the user's query, with the appropriate action taken. "
                "If the command involved a directory change, make sure to include the new directory path."
            )
        )
        
        # Use sequential process instead of hierarchical to simplify delegation
        crew = Crew(
            agents=[terminal_agent, file_nav_agent, code_exec_agent, web_research_agent, pdf_analyst_agent], # Add PDF agent to crew
            tasks=[task],
            verbose=True,
            knowledge=self._create_knowledge_sources(),
            process=Process.sequential  # Change to sequential process
        )
        
        return crew

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
        directory = command.strip()[3:].trip()
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

    def terminal_assistant_sync(self, command: str) -> str:
        """Synchronous version of terminal assistant to avoid asyncio conflicts."""
        try:
            # For now, use the existing crew-based approach without flows
            # This avoids the asyncio conflicts while we stabilize the system
            
            # Basic input validation
            if not command or not command.strip():
                return "Please provide a command or question."
            
            command = command.strip()
            command_lower = command.lower() # For case-insensitive checks
            
            # Handle help requests
            if command_lower in ['help', 'commands', 'what can you do']:
                return self._get_help_message()

            # Handle 'cd' command explicitly
            if command_lower.startswith("cd "):
                return self._handle_cd_command(command)

            # Handle simple file operations
            if any(cmd_keyword in command_lower for cmd_keyword in ['ls', 'list', 'directory', 'files']):
                # Avoid overly broad matches, e.g. "list my favorite pdf files"
                # This simple check might need refinement for more complex natural language.
                # For now, if it's not a direct shell command, let the crew handle it.
                if self._is_simple_shell_command(command) or command_lower == "ls": # specifically allow 'ls'
                     return self._handle_file_listing(command)
            
            # Handle direct shell commands
            if self._is_simple_shell_command(command):
                return self._execute_simple_command(command)
            
            # Handle other commands through the crew system
            return self._run_with_crew_sync(command)
            
        except Exception as e:
            return f"Error processing command: {str(e)}"
    
    def _get_help_message(self) -> str:
        """Get help message for available commands."""
        return """
CodexSimulator Terminal Assistant

Available capabilities:
• File operations: ls, cat, find files
• Code execution: run Python scripts, analyze code
• Web research: search information, get weather
• System commands: basic shell operations
• General assistance: ask questions, get explanations

Example commands:
• "list files in current directory"
• "run this Python script"
• "search for information about AI"
• "what's the weather like?"
• "explain how this code works"

Type 'exit' or 'quit' to exit.
        """
    
    def _handle_file_listing(self, command: str) -> str:
        """Handle file listing operations."""
        try:
            import os
            current_dir = os.getcwd()
            files = []
            
            for item in os.listdir(current_dir):
                if os.path.isfile(item):
                    files.append(f"📄 {item}")
                elif os.path.isdir(item):
                    files.append(f"📁 {item}")
            
            if files:
                return f"Contents of {current_dir}:\n" + "\n".join(files)
            else:
                return f"Directory {current_dir} is empty."
                
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def _is_simple_shell_command(self, command: str) -> bool:
        """Check if this is a simple shell command that can be executed directly."""
        simple_commands = ['ls', 'pwd', 'cat', 'echo', 'date', 'whoami', 'which']
        cmd_parts = command.strip().split()
        return len(cmd_parts) > 0 and cmd_parts[0] in simple_commands
    
    def _execute_simple_command(self, command: str) -> str:
        """Execute simple commands directly without full crew overhead."""
        try:
            import subprocess
            
            # Basic safety check
            if any(dangerous in command.lower() for dangerous in ['rm ', 'del ', 'format ', 'sudo ']):
                return "Command blocked for safety. Use the crew system for complex operations."
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.cwd
            )
            
            if result.returncode == 0:
                return result.stdout.strip() if result.stdout.strip() else "Command executed successfully (no output)"
            else:
                return f"Command failed with exit code {result.returncode}: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def _run_with_crew_sync(self, command: str) -> str:
        """Run command through crew system synchronously."""
        try:
            # Ensure CLAUDE.md exists for shared state
            self._ensure_claude_md_exists()
            user_context = self._load_user_context()
            claude_context = self._load_claude_context()

            # Use the specific terminal crew setup
            terminal_crew = self._create_terminal_crew(command, user_context, claude_context)

            # Prepare inputs for the terminal_commander's task and potential delegated tasks.
            # The main task description in _create_terminal_crew already embeds command, cwd, etc.
            # These inputs are available if template variables are used or for context.
            inputs = {
                'user_command': command,
                'cwd': self.cwd,
                'user_context': user_context,
                'claude_context': claude_context,
                # Add other common variables, ensuring defaults if not always applicable
                'current_year': str(datetime.now().year),
                'topic': command, # Default topic to the command itself
                'file_request': 'N/A',
                'code_snippet': 'N/A',
                'search_query': command, # Default search query
                'pdf_path': 'N/A', # Default for analyze_pdf_task if delegated
                'user_query_about_pdf': 'N/A' # Default for analyze_pdf_task if delegated
            }
            
            result = terminal_crew.kickoff(inputs=inputs)
            
            # Extract the result properly
            raw_output = ""
            if hasattr(result, 'raw_output') and result.raw_output is not None: # CrewAI >= 0.28.8
                raw_output = str(result.raw_output)
            elif hasattr(result, 'raw') and result.raw is not None: # Older CrewAI
                raw_output = str(result.raw)
            elif hasattr(result, 'result') and result.result is not None:
                raw_output = str(result.result)
            elif result is not None:
                raw_output = str(result)
            
            # Update CWD if changed by the command execution
            new_cwd = self._state.extract_cwd_from_response(raw_output)
            if new_cwd:
                self.cwd = new_cwd # This uses the setter which updates state_tracker

            # Update shared memory (CLAUDE.md)
            self._update_claude_md(command, raw_output)
            
            return raw_output
                
        except Exception as e:
            error_msg = f"Error executing command via crew: {str(e)}"
            # Optionally log to CLAUDE.md
            self._update_claude_md(command, f"CREW_EXECUTION_ERROR: {error_msg}")
            return error_msg
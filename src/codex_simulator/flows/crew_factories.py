import asyncio
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from ..flows.state_manager import LocationData # Import LocationData
from ..mcp import MCPClient, wrap_tools_with_mcp
from ..tools import (
    SafeDirectoryTool, SafeFileReadTool, SafeFileWriteTool,
    SafeShellTool, SerpAPITool, WebsiteTool
)
from ..tools.delegate_tool import DelegateTool, MCPDelegateTool

class CrewFactory:
    """Factory for creating specialized crews with optional MCP integration"""
    
    def __init__(self, llm, use_mcp: bool = False, mcp_client: Optional[MCPClient] = None):
        self.llm = llm
        self.use_mcp = use_mcp
        self.mcp_client = mcp_client
    
    def _wrap_tools_if_mcp(self, tools: List[Any]) -> List[Any]:
        """Wrap tools with MCP if enabled"""
        if self.use_mcp and self.mcp_client and tools:
            tool_names = [getattr(tool, 'name', str(tool)) for tool in tools]
            return wrap_tools_with_mcp(tool_names, self.mcp_client)
        return tools
    
    def create_file_crew(self, context: Dict[str, Any]) -> Crew:
        """Create a crew specialized for file operations with MCP support"""
        
        tools = [
            SafeDirectoryTool(),
            SafeFileReadTool(), 
            SafeFileWriteTool()
        ]
        
        # Wrap with MCP if enabled
        tools = self._wrap_tools_if_mcp(tools)
        
        file_navigator = Agent(
            role='Expert File System Navigator',
            goal='Perform file operations efficiently and safely',
            backstory="""You are an expert in file system operations with extensive knowledge 
            of directory navigation, file manipulation, and system organization.""",
            tools=tools,
            verbose=True,
            llm=self.llm
        )
        
        file_task = Task(
            description=context.get('command', 'Perform file operation'),
            expected_output="File operation completed with results",
            agent=file_navigator
        )
        
        crew = Crew(
            agents=[file_navigator],
            tasks=[file_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Add MCP context if available
        if self.use_mcp and self.mcp_client:
            asyncio.create_task(self._update_mcp_context(context))
        
        return crew
    
    def create_code_crew(self, context: Dict[str, Any]) -> Crew:
        """Create a crew specialized for code execution with MCP support"""
        
        tools = [SafeShellTool(), SafeFileReadTool(), SafeFileWriteTool()]
        tools = self._wrap_tools_if_mcp(tools)
        
        code_executor = Agent(
            role='Secure Code Execution Specialist',
            goal='Execute code and commands safely with performance monitoring',
            backstory="""You are a security-focused code execution expert with deep knowledge 
            of sandboxing, performance optimization, and safe execution practices.""",
            tools=tools,
            verbose=True,
            llm=self.llm
        )
        
        code_task = Task(
            description=context.get('command', 'Execute code or command'),
            expected_output="Code execution completed with results and performance metrics",
            agent=code_executor
        )
        
        crew = Crew(
            agents=[code_executor],
            tasks=[code_task],
            verbose=True,
            process=Process.sequential
        )
        
        if self.use_mcp and self.mcp_client:
            asyncio.create_task(self._update_mcp_context(context))
        
        return crew
    
    def create_web_crew(self, context: Dict[str, Any]) -> Crew:
        """Create a crew specialized for web research with MCP support"""
        
        tools = [SerpAPITool(), WebsiteTool()]
        tools = self._wrap_tools_if_mcp(tools)
        
        web_researcher = Agent(
            role='Expert Web Research Specialist',
            goal='Conduct thorough research and gather accurate information',
            backstory="""You are an expert researcher with exceptional skills in finding, 
            evaluating, and synthesizing information from diverse web sources.""",
            tools=tools,
            verbose=True,
            llm=self.llm
        )
        
        research_task = Task(
            description=context.get('command', 'Conduct web research'),
            expected_output="Comprehensive research results with sources and analysis",
            agent=web_researcher
        )
        
        crew = Crew(
            agents=[web_researcher],
            tasks=[research_task],
            verbose=True,
            process=Process.sequential
        )
        
        if self.use_mcp and self.mcp_client:
            asyncio.create_task(self._update_mcp_context(context))
        
        return crew
    
    def create_terminal_crew(self, context: Dict[str, Any]) -> Crew:
        """Create a comprehensive crew for general terminal operations."""
        
        # Create agents
        agents_dict = {}
        
        file_agent = Agent(
            role="File System Operations Expert",
            goal="Navigate file systems, read files, and manage directories safely",
            backstory="I am an expert in file system operations.",
            tools=[SafeDirectoryTool(), SafeFileReadTool(), SafeFileWriteTool()],
            llm=self.llm,
            verbose=True
        )
        agents_dict["File System Operations Expert"] = file_agent
        
        code_agent = Agent(
            role="Secure Code and Command Execution Specialist", 
            goal="Execute code and commands safely",
            backstory="I specialize in secure code execution.",
            tools=[SafeShellTool(), SafeFileReadTool(), SafeFileWriteTool()],
            llm=self.llm,
            verbose=True
        )
        agents_dict["Secure Code and Command Execution Specialist"] = code_agent
        
        research_agent = Agent(
            role="Internet Research Analyst",
            goal="Conduct web searches and provide information",
            backstory="I am an expert researcher.",
            tools=[SerpAPITool(), WebsiteTool()],
            llm=self.llm,
            verbose=True
        )
        agents_dict["Internet Research Analyst"] = research_agent
        
        # Choose delegation tool based on MCP availability
        if self.use_mcp and self.mcp_client:
            delegate_tool = MCPDelegateTool(agents_dict=agents_dict, mcp_client=self.mcp_client)
        else:
            delegate_tool = DelegateTool(agents_dict=agents_dict)
        
        # Create terminal commander
        terminal_agent = Agent(
            role="Terminal Command Orchestrator and AI Assistant",
            goal="Understand user commands and delegate to appropriate specialists",
            backstory="I coordinate between specialized agents to handle complex requests.",
            tools=[delegate_tool],
            llm=self.llm,
            verbose=True
        )
        
        # Create task
        task = Task(
            description=f"Handle this request: {context.get('command', 'No command specified')}",
            agent=terminal_agent,
            expected_output="A comprehensive response addressing the user's request."
        )
        
        all_agents = [terminal_agent, file_agent, code_agent, research_agent]
        
        return Crew(
            agents=all_agents,
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
    
    async def _update_mcp_context(self, context: Dict[str, Any]):
        """Update MCP server with current context"""
        if self.mcp_client:
            try:
                await self.mcp_client.update_state(
                    state_updates={
                        "current_command": context.get('command', ''),
                        "cwd": context.get('cwd', ''),
                        "timestamp": context.get('timestamp', ''),
                        "context_data": context
                    },
                    scope="session"
                )
            except Exception as e:
                print(f"Failed to update MCP context: {e}")

    @staticmethod
    def create_file_operations_crew(state_context: Dict) -> Crew:
        """Create a crew optimized for file operations"""
        from ..crew import CodexSimulator
        
        # Create a temporary simulator instance to access agents
        simulator = CodexSimulator()
        
        file_navigator = simulator.file_navigator()
        
        command = state_context.get('command', '')
        cwd = state_context.get('cwd', '')
        current_location = state_context.get('current_location')
        
        task_description = f"Handle file operation: '{command}'. Current directory: '{cwd}'."
        if current_location and current_location.address:
            task_description += f" User's current location context: {current_location.address}."
        
        # Create a file operation task
        file_task = Task(
            description=task_description,
            expected_output="File operation result with any directory changes noted",
            agent=file_navigator
        )
        
        return Crew(
            agents=[file_navigator],
            tasks=[file_task],
            process=Process.sequential,
            verbose=True
        )
    
    @staticmethod
    def create_code_execution_crew(command: str, safety_checks: bool = True, safety_level: str = "high", current_location: Optional[LocationData] = None, location_permission: Optional[str] = None) -> Crew:
        """Create a crew for safe code execution"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()
        
        task_description = f"Execute the following code or command safely: '{command}'. Safety checks enabled: {safety_checks}."
        if current_location and current_location.address and location_permission != "denied":
            task_description += f" User's current location context: {current_location.address} (Permission: {location_permission})."

        execution_task = Task(
            description=task_description,
            expected_output="Execution results with output and any errors",
            agent=code_executor
        )
        
        return Crew(
            agents=[code_executor],
            tasks=[execution_task],
            process=Process.sequential,
            verbose=True
        )
    
    @staticmethod
    def create_research_crew(query: str, depth: str = "standard", current_location: Optional[LocationData] = None, location_permission: Optional[str] = None) -> Crew:
        """Create a crew for web research tasks"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        web_researcher = simulator.web_researcher()

        task_description = f"Research the query: '{query}' (depth: {depth})"
        if current_location and current_location.address and location_permission != "denied":
            task_description += f" considering the user's current location: {current_location.address}."
        task_description += " Provide relevant information."
        
        research_task = Task(
            description=task_description,
            expected_output="Research results with sources and key findings",
            agent=web_researcher
        )
        
        return Crew(
            agents=[web_researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
    
    @staticmethod
    def create_code_analysis_crew(command: str, analysis_type: str = 'code_review', current_location: Optional[LocationData] = None, location_permission: Optional[str] = None) -> Crew:
        """Create a crew specialized for code analysis and debugging"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()
        file_navigator = simulator.file_navigator()
        
        task_description = f"Analyze the following code or command: '{command}'. Analysis type: '{analysis_type}'. Focus on functionality, performance, and potential issues."
        if current_location and current_location.address and location_permission != "denied":
            task_description += f" User's current location context: {current_location.address} (Permission: {location_permission})."

        analysis_task = Task(
            description=task_description,
            expected_output="Detailed code analysis with explanations and recommendations",
            agent=code_executor
        )
        
        return Crew(
            agents=[code_executor, file_navigator],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
    
    @staticmethod
    def create_workflow_crew(command: str, workflow_type: str = 'multi_step', current_directory: str = '', current_location: Optional[LocationData] = None, location_permission: Optional[str] = None) -> Crew:
        """Create a crew for handling complex multi-step workflows"""
        from ..crew import CodexSimulator, remove_competing_delegation_tools # Import the cleanup utility
        
        simulator = CodexSimulator()
        terminal_agent = simulator.terminal_commander()
        file_navigator = simulator.file_navigator()
        code_executor = simulator.code_executor()
        
        # Initial cleanup of manager agent's tools before crew creation
        remove_competing_delegation_tools(terminal_agent)
        terminal_agent.tools = [] 
        
        # Clean worker agents as well
        remove_competing_delegation_tools(file_navigator)
        remove_competing_delegation_tools(code_executor)

        # Worker agents for the hierarchical crew
        worker_agents = [file_navigator, code_executor]
        worker_agent_names = [agent.role for agent in worker_agents]

        task_description = (
            f"Execute complex multi-step workflow for command: '{command}'.\n"
            f"Workflow type: '{workflow_type}'.\n"
            f"Current directory for context: '{current_directory}'.\n"
        )
        if current_location and current_location.address and location_permission != "denied":
            task_description += f"User's current location context: {current_location.address} (Permission: {location_permission}).\n\n"
        else:
            task_description += "\n"

        task_description += (
            f"CRITICAL INSTRUCTION FOR MANAGER (YOU - {terminal_agent.role}): \n"
            f"You are a manager. Your role is to understand the overall task and break it down into sub-tasks. "
            f"Delegate these sub-tasks to your specialist coworkers by clearly stating WHICH coworker should perform WHICH sub-task in your thought process. "
            f"You do NOT have an explicit 'delegate' tool; your delegation is through natural language instructions specifying the coworker and the sub-task. "
            f"Your available specialist coworkers are: {', '.join(worker_agent_names)}.\n"
            f"After receiving results from your coworkers, synthesize them into a final, comprehensive answer for the user."
        )
        
        workflow_task = Task(
            description=task_description,
            expected_output="Completed workflow with results from all steps, synthesized into a final answer.",
            agent=terminal_agent # The task is assigned to the manager agent
        )
        
        crew = Crew(
            agents=worker_agents, # Only worker agents here
            tasks=[workflow_task],
            process=Process.hierarchical,
            manager_llm=terminal_agent.llm, # Use manager's LLM for consistency
            manager_agent=terminal_agent, # Manager agent specified here
            verbose=True
        )

        # Crucial step: Clean tools from the manager_agent *after* crew instantiation
        # This handles tools CrewAI might add during hierarchical setup.
        if crew.manager_agent:
            remove_competing_delegation_tools(crew.manager_agent)
            crew.manager_agent.tools = []
            print(f"Tools for manager_agent '{crew.manager_agent.role}' cleared after crew creation.")
        
        return crew
    
    @staticmethod
    def create_system_monitoring_crew(command: str, monitoring_type: str = 'system_info', current_location: Optional[LocationData] = None, location_permission: Optional[str] = None) -> Crew:
        """Create a crew for system monitoring and performance analysis"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()  # Has shell access for system commands
        performance_monitor = simulator.performance_monitor()
        
        task_description = f"Monitor system based on command: '{command}'. Monitoring type: '{monitoring_type}'."
        if current_location and current_location.address and location_permission != "denied":
            task_description += f" User's current location context: {current_location.address} (Permission: {location_permission})."
        task_description += " Provide detailed system information and performance metrics."

        monitoring_task = Task(
            description=task_description,
            expected_output="System performance metrics and analysis",
            agent=performance_monitor
        )
        
        return Crew(
            agents=[performance_monitor, code_executor],
            tasks=[monitoring_task],
            process=Process.sequential,
            verbose=True
        )

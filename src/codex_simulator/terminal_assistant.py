"""
Enhanced Terminal Assistant with improved agent architecture
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task

# Import all tool classes
from .tools.safe_directory_tool import SafeDirectoryTool
from .tools.safe_file_read_tool import SafeFileReadTool
from .tools.safe_shell_tool import SafeShellTool
from .tools.execution_profiler_tool import ExecutionProfilerTool
from .tools.pdf_reader_tool import PDFReaderTool
from .tools.new_tools import (
    EnvironmentVariableTool,
    StaticCodeAnalysisTool,
    GitManagementTool,
    NetworkDiagnosticTool,
    PlottingTool,
    SystemMonitoringTool
)

# Web tools (optional imports)
try:
    from .tools.serp_api_tool import SerpAPITool
    from .tools.website_tool import WebsiteTool
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    WEB_TOOLS_AVAILABLE = False
    logging.warning("Web tools not available - SerpAPI or Website tools not configured")

@CrewBase
class TerminalAssistantCrew:
    """Enhanced Terminal Assistant with comprehensive agent architecture"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        super().__init__()
        self.current_working_directory = os.getcwd()
        self.session_context = {
            'start_time': datetime.now(),
            'commands_executed': 0,
            'last_command': None,
            'user_preferences': {}
        }
    
    # Core Terminal Agents
    @agent
    def terminal_commander(self) -> Agent:
        """Main coordination agent for terminal operations"""
        return Agent(
            config=self.agents_config['terminal_commander'],
            tools=[],  # Commander delegates, doesn't use tools directly
            max_execution_time=120,
            step_callback=self._log_agent_step
        )
    
    @agent
    def file_navigator(self) -> Agent:
        """File system operations specialist"""
        tools = [
            SafeDirectoryTool(),
            SafeFileReadTool(),
            PDFReaderTool()
        ]
        return Agent(
            config=self.agents_config['file_navigator'],
            tools=tools,
            max_execution_time=60
        )
    
    @agent
    def code_executor(self) -> Agent:
        """Secure code and command execution specialist"""
        tools = [
            SafeShellTool(),
            ExecutionProfilerTool()
        ]
        return Agent(
            config=self.agents_config['code_executor'],
            tools=tools,
            max_execution_time=120
        )
    
    @agent
    def web_researcher(self) -> Agent:
        """Web research and information gathering specialist"""
        tools = []
        if WEB_TOOLS_AVAILABLE:
            tools.extend([SerpAPITool(), WebsiteTool()])
        return Agent(
            config=self.agents_config['web_researcher'],
            tools=tools,
            max_execution_time=90
        )
    
    @agent
    def performance_monitor(self) -> Agent:
        """System performance and monitoring specialist"""
        tools = [
            SystemMonitoringTool(),
            ExecutionProfilerTool(),
            PlottingTool()
        ]
        return Agent(
            config=self.agents_config['performance_monitor'],
            tools=tools,
            max_execution_time=60
        )
    
    # Specialized Agents
    @agent
    def environment_manager(self) -> Agent:
        """Environment and configuration management"""
        tools = [EnvironmentVariableTool()]
        return Agent(
            config=self.agents_config['environment_manager'],
            tools=tools,
            max_execution_time=30
        )
    
    @agent
    def security_analyst(self) -> Agent:
        """Security analysis and code review"""
        tools = [StaticCodeAnalysisTool()]
        return Agent(
            config=self.agents_config['security_analyst'],
            tools=tools,
            max_execution_time=90
        )
    
    @agent
    def git_manager(self) -> Agent:
        """Git repository and version control management"""
        tools = [GitManagementTool()]
        return Agent(
            config=self.agents_config['git_manager'],
            tools=tools,
            max_execution_time=60
        )
    
    @agent
    def network_analyst(self) -> Agent:
        """Network diagnostics and connectivity"""
        tools = [NetworkDiagnosticTool()]
        return Agent(
            config=self.agents_config['network_analyst'],
            tools=tools,
            max_execution_time=60
        )
    
    # Research Agents
    @agent
    def researcher(self) -> Agent:
        """Senior research specialist"""
        tools = []
        if WEB_TOOLS_AVAILABLE:
            tools.extend([SerpAPITool(), WebsiteTool()])
        return Agent(
            config=self.agents_config['researcher'],
            tools=tools,
            max_execution_time=120
        )
    
    @agent
    def reporting_analyst(self) -> Agent:
        """Research reporting and documentation"""
        return Agent(
            config=self.agents_config['reporting_analyst'],
            tools=[],
            max_execution_time=90
        )
    
    # Core Tasks
    @task
    def process_command_task(self) -> Task:
        """Main command processing task"""
        return Task(
            config=self.tasks_config['process_command_task'],
            agent=self.terminal_commander,
            output_file="terminal_session.log"
        )
    
    @task
    def navigate_files_task(self) -> Task:
        """File navigation and management task"""
        return Task(
            config=self.tasks_config['navigate_files_task'],
            agent=self.file_navigator
        )
    
    @task
    def execute_code_task(self) -> Task:
        """Code and command execution task"""
        return Task(
            config=self.tasks_config['execute_code_task'],
            agent=self.code_executor
        )
    
    @task
    def web_search_task(self) -> Task:
        """Web research task"""
        return Task(
            config=self.tasks_config['web_search_task'],
            agent=self.web_researcher
        )
    
    @task
    def system_monitor_task(self) -> Task:
        """System monitoring task"""
        return Task(
            config=self.tasks_config['system_monitor_task'],
            agent=self.performance_monitor
        )
    
    # Specialized Tasks
    @task
    def manage_environment_task(self) -> Task:
        """Environment management task"""
        return Task(
            config=self.tasks_config['manage_environment_task'],
            agent=self.environment_manager
        )
    
    @task
    def security_analysis_task(self) -> Task:
        """Security analysis task"""
        return Task(
            config=self.tasks_config['security_analysis_task'],
            agent=self.security_analyst
        )
    
    @task
    def git_operation_task(self) -> Task:
        """Git operations task"""
        return Task(
            config=self.tasks_config['git_operation_task'],
            agent=self.git_manager
        )
    
    @task
    def network_diagnostic_task(self) -> Task:
        """Network diagnostics task"""
        return Task(
            config=self.tasks_config['network_diagnostic_task'],
            agent=self.network_analyst
        )
    
    @task
    def create_visualization_task(self) -> Task:
        """Data visualization task"""
        return Task(
            config=self.tasks_config['create_visualization_task'],
            agent=self.performance_monitor
        )
    
    # Research Tasks
    @task
    def comprehensive_research_task(self) -> Task:
        """Comprehensive research task"""
        return Task(
            config=self.tasks_config['comprehensive_research_task'],
            agent=self.researcher
        )
    
    @task
    def generate_report_task(self) -> Task:
        """Report generation task"""
        return Task(
            config=self.tasks_config['generate_report_task'],
            agent=self.reporting_analyst
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the terminal assistant crew with hierarchical process"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.terminal_commander,
            verbose=True,
            memory=True,
            max_execution_time=300,
            step_callback=self._log_step
        )
    
    def _log_agent_step(self, step):
        """Log agent execution steps"""
        logging.info(f"Agent step: {step}")
    
    def _log_step(self, step):
        """Log crew execution steps"""
        logging.info(f"Crew step: {step}")
    
    def update_working_directory(self, new_cwd: str):
        """Update the current working directory"""
        if os.path.exists(new_cwd) and os.path.isdir(new_cwd):
            self.current_working_directory = os.path.abspath(new_cwd)
            os.chdir(self.current_working_directory)
            return True
        return False
    
    def get_session_context(self) -> str:
        """Get formatted session context"""
        return f"""
Session Info:
- Start Time: {self.session_context['start_time']}
- Commands Executed: {self.session_context['commands_executed']}
- Last Command: {self.session_context.get('last_command', 'None')}
- Current Directory: {self.current_working_directory}
"""
    
    def process_terminal_command(self, user_command: str) -> str:
        """Process a terminal command through the crew"""
        try:
            # Update session context
            self.session_context['commands_executed'] += 1
            self.session_context['last_command'] = user_command
            
            # Prepare context for the crew
            context = {
                'user_command': user_command,
                'cwd': self.current_working_directory,
                'user_context': self.get_session_context(),
                'current_year': datetime.now().year
            }
            
            # Execute the crew with the command
            result = self.crew().kickoff(inputs=context)
            
            return str(result)
            
        except Exception as e:
            error_msg = f"Error processing command '{user_command}': {str(e)}"
            logging.error(error_msg)
            return error_msg

def create_terminal_assistant() -> TerminalAssistantCrew:
    """Factory function to create a terminal assistant instance"""
    return TerminalAssistantCrew()

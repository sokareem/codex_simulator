from crewai import Agent, Crew, Task, Process
from .agent_factory import AgentFactory
from ..tools.delegate_tool import DelegateTool

class TerminalCrewBuilder:
    """Builder for terminal command processing crews"""
    
    def __init__(self, llm, agent_factory: AgentFactory):
        self.llm = llm
        self.agent_factory = agent_factory
    
    def create_terminal_crew(self, command: str, user_context: str, codex_context: str, cwd: str, command_history: list) -> Crew:
        """Create a dedicated crew for handling terminal commands"""
        
        # Create agents
        terminal_agent = self._create_terminal_commander()
        file_nav_agent = self.agent_factory.create_file_navigator()
        code_exec_agent = self.agent_factory.create_code_executor()
        web_research_agent = self.agent_factory.create_web_researcher()
        pdf_analyst_agent = self.agent_factory.create_pdf_analyst()
        translation_agent = self.agent_factory.create_translator()
        software_architect_agent = self.agent_factory.create_software_architect()
        systems_thinker_agent = self.agent_factory.create_systems_thinker()
        data_analyst_agent = self.agent_factory.create_data_analyst()
        
        # Create agent registry for delegation
        agent_registry = {
            "FileNavigator": file_nav_agent,
            "CodeExecutor": code_exec_agent,
            "WebResearcher": web_research_agent,
            "PDFDocumentAnalyst": pdf_analyst_agent,
            "MultilingualTranslator": translation_agent,
            "SoftwareArchitect": software_architect_agent,
            "SystemsThinker": systems_thinker_agent,
            "DataAnalyst": data_analyst_agent
        }
        
        # Add delegation tool to terminal commander
        delegate_tool = DelegateTool(agents_dict=agent_registry)
        terminal_agent.tools = [delegate_tool]
        
        # Create task
        task = self._create_terminal_task(terminal_agent, command, user_context, codex_context, cwd, command_history)
        
        # Create crew
        all_agents = [terminal_agent, file_nav_agent, code_exec_agent, web_research_agent, 
                     pdf_analyst_agent, translation_agent, software_architect_agent, 
                     systems_thinker_agent, data_analyst_agent]
        
        crew = Crew(
            agents=all_agents,
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        return crew
    
    def _create_terminal_commander(self) -> Agent:
        """Create terminal commander agent without tools (manager role)"""
        return Agent(
            role='Terminal Command Orchestrator and AI Assistant',
            goal='Coordinate and delegate tasks to specialist agents',
            backstory='Intelligent terminal assistant and command orchestrator',
            tools=[],  # No tools - will be added later
            verbose=True,
            llm=self.llm
        )
    
    def _create_terminal_task(self, agent, command: str, user_context: str, codex_context: str, cwd: str, command_history: list):
        """Create terminal processing task"""
        task_description = (
            f"Process the user's terminal command or query: '{command}'\n\n"
            f"Current working directory: {cwd}\n"
            f"User context: {user_context}\n"
            f"Command history: {', '.join(command_history[-5:]) if command_history else 'None'}\n"
            f"Session context: {codex_context[:1000] + '...' if len(codex_context) > 1000 else codex_context}\n\n"
            f"Available specialists: FileNavigator, CodeExecutor, WebResearcher, PDFDocumentAnalyst, "
            f"MultilingualTranslator, SoftwareArchitect, SystemsThinker, DataAnalyst.\n"
            f"Delegate tasks appropriately and synthesize results for the user."
        )
        
        return Task(
            description=task_description,
            agent=agent,
            expected_output="Clear and helpful response to the user's query with appropriate action taken"
        )

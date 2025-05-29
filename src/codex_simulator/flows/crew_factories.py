from typing import Dict, Any
from crewai import Crew, Process, Agent, Task

class CrewFactory:
    """Factory for creating specialized crews within flows"""
    
    @staticmethod
    def create_file_operations_crew(state_context: Dict) -> Crew:
        """Create a crew optimized for file operations"""
        from ..crew import CodexSimulator
        
        # Create a temporary simulator instance to access agents
        simulator = CodexSimulator()
        
        file_navigator = simulator.file_navigator()
        
        command = state_context.get('command', '')
        cwd = state_context.get('cwd', '')
        
        # Create a file operation task
        file_task = Task(
            description=f"Handle file operation: '{command}'. Current directory: '{cwd}'",
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
    def create_code_execution_crew(command: str, safety_checks: bool = True, safety_level: str = "high") -> Crew:
        """Create a crew for safe code execution"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()
        
        execution_task = Task(
            description=f"Execute the following code or command safely: '{command}'. Safety checks enabled: {safety_checks}.",
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
    def create_research_crew(query: str, depth: str = "standard") -> Crew:
        """Create a crew for web research tasks"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        web_researcher = simulator.web_researcher()
        
        research_task = Task(
            description=f"Research the query: '{query}' (depth: {depth}) and provide relevant information.",
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
    def create_code_analysis_crew(command: str, analysis_type: str = 'code_review') -> Crew:
        """Create a crew specialized for code analysis and debugging"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()
        file_navigator = simulator.file_navigator()
        
        analysis_task = Task(
            description=f"Analyze the following code or command: '{command}'. Analysis type: '{analysis_type}'. Focus on functionality, performance, and potential issues.",
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
    def create_workflow_crew(command: str, workflow_type: str = 'multi_step', current_directory: str = '') -> Crew:
        """Create a crew for handling complex multi-step workflows"""
        from ..crew import CodexSimulator, remove_competing_delegation_tools # Import the cleanup utility
        
        simulator = CodexSimulator()
        terminal_agent = simulator.terminal_commander()
        file_navigator = simulator.file_navigator()
        code_executor = simulator.code_executor()
        
        # Ensure manager agent has no delegation tools for hierarchical process
        remove_competing_delegation_tools(terminal_agent)
        terminal_agent.tools = [] # Explicitly clear tools for the manager
        
        # Clean worker agents as well
        remove_competing_delegation_tools(file_navigator)
        remove_competing_delegation_tools(code_executor)

        # Worker agents for the hierarchical crew
        worker_agents = [file_navigator, code_executor]
        worker_agent_names = [agent.role for agent in worker_agents]

        task_description = (
            f"Execute complex multi-step workflow for command: '{command}'.\n"
            f"Workflow type: '{workflow_type}'.\n"
            f"Current directory for context: '{current_directory}'.\n\n"
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
        
        return Crew(
            agents=worker_agents, # Only worker agents here
            tasks=[workflow_task],
            process=Process.hierarchical,
            manager_llm=terminal_agent.llm, # Use manager's LLM for consistency
            manager_agent=terminal_agent, # Manager agent specified here
            verbose=True
        )
    
    @staticmethod
    def create_system_monitoring_crew(command: str, monitoring_type: str = 'system_info') -> Crew:
        """Create a crew for system monitoring and performance analysis"""
        from ..crew import CodexSimulator
        
        simulator = CodexSimulator()
        code_executor = simulator.code_executor()  # Has shell access for system commands
        performance_monitor = simulator.performance_monitor()
        
        monitoring_task = Task(
            description=f"Monitor system based on command: '{command}'. Monitoring type: '{monitoring_type}'. Provide detailed system information and performance metrics.",
            expected_output="System performance metrics and analysis",
            agent=performance_monitor
        )
        
        return Crew(
            agents=[performance_monitor, code_executor],
            tasks=[monitoring_task],
            process=Process.sequential,
            verbose=True
        )

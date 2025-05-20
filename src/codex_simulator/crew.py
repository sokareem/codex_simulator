from crewai import Agent, Crew, Process, Task, Knowledge
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain.schema.messages import SystemMessage
from typing import Dict, List
import os
from datetime import datetime
import dotenv

# Import the custom LLM
from .llms.custom_gemini_llm import CustomGeminiLLM

# Explicitly import the tools we need
from codex_simulator.tools.safe_shell_tool import SafeShellTool
from codex_simulator.tools.safe_directory_tool import SafeDirectoryTool
from codex_simulator.tools.safe_file_read_tool import SafeFileReadTool
from codex_simulator.tools.serp_api_tool import SerpAPITool
from codex_simulator.tools.website_tool import WebsiteTool

# Load environment variables
dotenv.load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CodexSimulator():
    """CodexSimulator crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # State variables
    cwd: str = os.getcwd()
    command_history: List[str] = []
    
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
            model=model_env_name, # Ensure this matches the field name in CustomGeminiLLM
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
    
    # Claude Terminal Assistant agents
    @agent
    def terminal_commander(self) -> Agent:
        return Agent(
            config=self.agents_config['terminal_commander'],
            llm=self._get_llm(),
            verbose=True
        )
    
    @agent
    def file_navigator(self) -> Agent:
        return Agent(
            config=self.agents_config['file_navigator'],
            llm=self._get_llm(),
            tools=[
                SafeDirectoryTool(),
                SafeFileReadTool(),
                SafeShellTool(allowed_commands=["ls", "pwd", "find", "grep", "cat", "head", "tail", "wc"])
            ],
            verbose=True
        )
    
    @agent
    def code_executor(self) -> Agent:
        return Agent(
            config=self.agents_config['code_executor'],
            llm=self._get_llm(),
            tools=[
                SafeShellTool(
                    allowed_commands=["python", "pip", "node", "npm", "echo", "cat", "mkdir", "cp", "touch"]
                )
            ],
            verbose=True
        )
    
    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],
            llm=self._get_llm(),
            tools=[
                SerpAPITool(),   # for search‐engine queries
                WebsiteTool()    # for fetching & crawling page content
            ],
            verbose=True
        )

    # Original tasks
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
    
    # Claude Terminal Assistant tasks
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

    @crew
    def crew(self) -> Crew:
        """Creates the CodexSimulator crew"""
        # Properly create a Knowledge object instead of passing a list of paths
        knowledge = None
        try:
            # Check if the knowledge file exists before creating Knowledge object
            if os.path.exists("knowledge/user_preference.txt"):
                knowledge = Knowledge(
                    documents=["knowledge/user_preference.txt"]
                )
        except Exception as e:
            print(f"Warning: Could not load knowledge: {e}")
        
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            llm=self._get_llm(),  # Use Gemini for the manager LLM as well
            verbose=True,
            knowledge=knowledge,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

    def _create_terminal_crew(self, command: str, user_context: str) -> Crew:
        """Create a dedicated crew for handling terminal commands"""
        # Create the terminal commander agent
        terminal_agent = self.terminal_commander()
        
        # Create the process command task with the specific command
        task = Task(
            description=f"Process the user's terminal command or query: '{command}' " +
                       f"Current working directory is: {self.cwd} " +
                       f"User context: {user_context}",
            agent=terminal_agent,
            expected_output="A clear and helpful response to the user's query, with the appropriate action taken."
        )

        # Create a knowledge source if possible
        knowledge = None
        if os.path.exists("knowledge/user_preference.txt"):
            try:
                knowledge = Knowledge(
                    documents=["knowledge/user_preference.txt"]
                )
            except Exception:
                pass

        # Create a specific crew for this command
        return Crew(
            agents=[terminal_agent, self.file_navigator(), self.code_executor(), self.web_researcher()],
            tasks=[task],
            llm=self._get_llm(),  # Use Gemini for the manager LLM
            verbose=True,
            knowledge=knowledge,
            process=Process.sequential
        )
    
    def terminal_assistant(self, command: str) -> str:
        """Run the terminal assistant with a specific command"""
        self.command_history.append(command)
        
        # Load user preferences
        user_context = "No user context available"
        try:
            if os.path.exists("knowledge/user_preference.txt"):
                with open("knowledge/user_preference.txt", "r") as f:
                    user_context = f.read()
        except Exception as e:
            print(f"Warning: Could not load user preferences: {e}")
            
        # Handle cd command specially to update current working directory
        if command.strip().startswith("cd "):
            directory = command.strip()[3:].trip()
            new_dir = os.path.abspath(os.path.join(self.cwd, directory))
            if os.path.isdir(new_dir):
                self.cwd = new_dir
                return f"Changed directory to: {self.cwd}"
            else:
                return f"Directory not found: {directory}"
                
        # Handle basic pwd/directory query directly for efficiency
        if command.strip().lower() in ["pwd", "where am i", "what directory am i in", "current directory"]:
            return f"Current directory: {self.cwd}"
        
        try:
            # Create a specific crew for this command and run it
            terminal_crew = self._create_terminal_crew(command, user_context)
            inputs = {
                'user_command': command,
                'cwd': self.cwd,
                'user_context': user_context
            }
            result = terminal_crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            return f"Error processing command: {str(e)}"

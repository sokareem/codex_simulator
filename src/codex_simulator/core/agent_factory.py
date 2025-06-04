from typing import Dict, List, Any
from crewai import Agent
from ..tools import *
from ..utils.tool_adapter import patch_tool_methods

def remove_competing_delegation_tools(agent):
    """Remove competing delegation tools from agent"""
    if hasattr(agent, 'tools'):
        competing_tool_names = [
            'delegate', 'ask_question',
            'Delegate work to coworker', 'Ask question to coworker'
        ]
        competing_tool_names_lower = [name.lower() for name in competing_tool_names]
        
        original_tool_count = len(agent.tools)
        agent.tools = [
            t for t in agent.tools 
            if t.name.lower() not in competing_tool_names_lower
        ]
        
        if len(agent.tools) < original_tool_count:
            agent_name = agent.role if hasattr(agent, 'role') else 'Unknown Agent'
            print(f"Removed competing delegation tools from agent {agent_name}")

class AgentFactory:
    """Factory for creating specialized agents"""
    
    def __init__(self, llm, use_mcp=False, mcp_client=None):
        self.llm = llm
        self.use_mcp = use_mcp
        self.mcp_client = mcp_client
    
    def _create_tools(self, agent_type: str = "general") -> List[Any]:
        """Create tools for agents, optionally wrapping with MCP"""
        tools = []
        
        if agent_type == "file":
            tools = [
                SafeDirectoryTool(),
                SafeFileReadTool(),
                SafeFileWriteTool(),
                SafeShellTool(allowed_commands=[
                    "ls", "pwd", "find", "grep", "cat", "head", "tail", "wc", 
                    "du", "df", "stat", "file", "chmod"
                ]),
                FSCacheTool(),
                CSVReaderTool(),
            ]
        elif agent_type == "code":
            tools = [
                SafeShellTool(allowed_commands=[
                    "python", "python3", "pip", "pip3", "node", "npm", "yarn",
                    "echo", "cat", "mkdir", "cp", "touch", "stat", "file",
                    "ls", "test"
                ]),
                SafeFileReadTool(),
                SafeFileWriteTool(),
                ExecutionProfilerTool()
            ]
        elif agent_type == "web":
            tools = [
                SerpAPITool(),
                WebsiteTool(),
                SafeFileReadTool(),
                SafeFileWriteTool()
            ]
        elif agent_type == "pdf":
            tools = [PDFReaderTool()]
        elif agent_type == "translation":
            tools = [TranslationTool()]
        elif agent_type == "software_architect":
            tools = [SoftwareArchitectTool(), SafeFileReadTool(), SafeFileWriteTool()]
        elif agent_type == "systems_thinking":
            tools = [SystemsThinkingTool(), SafeFileReadTool(), SafeFileWriteTool()]
        elif agent_type == "data":
            tools = [CSVReaderTool(), SafeFileReadTool(), SafeFileWriteTool(), PDFReaderTool()]
        
        # MCP wrapping would go here if needed
        return tools
    
    def create_file_navigator(self) -> Agent:
        """Create the File Navigator agent"""
        agent = Agent(
            role='Expert File System Navigator and Operations Specialist',
            goal='Navigate file systems efficiently and perform file operations safely',
            backstory='Expert file system navigator with deep knowledge of Unix/Linux systems',
            tools=self._create_tools("file"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_code_executor(self) -> Agent:
        """Create the Code Executor agent"""
        agent = Agent(
            role='Secure Code and Command Execution Specialist',
            goal='Execute code and commands safely in controlled environments',
            backstory='Security-conscious code execution specialist',
            tools=self._create_tools("code"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_web_researcher(self) -> Agent:
        """Create the Web Researcher agent"""
        agent = Agent(
            role='Expert Web Research and Information Gathering Specialist',
            goal='Conduct thorough web research and gather accurate information',
            backstory='Expert researcher with exceptional web research skills',
            tools=self._create_tools("web"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_pdf_analyst(self) -> Agent:
        """Create the PDF Document Analyst agent"""
        agent = Agent(
            role='Expert PDF Document Analyst',
            goal='Read, analyze, summarize, and extract information from PDF documents',
            backstory='Specialist in handling PDF documents and extraction',
            tools=self._create_tools("pdf"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_translator(self) -> Agent:
        """Create the Multilingual Translator agent"""
        agent = Agent(
            role='Expert Multilingual Translator and Language Specialist',
            goal='Provide accurate translations with cultural context',
            backstory='Master linguist with expertise in 100+ languages',
            tools=self._create_tools("translation"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_software_architect(self) -> Agent:
        """Create the Software Architect agent"""
        agent = Agent(
            role='Senior Software Architect and Development Specialist',
            goal='Design robust software architectures and implement solutions',
            backstory='Seasoned software architect with extensive system design experience',
            tools=self._create_tools("software_architect"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_systems_thinker(self) -> Agent:
        """Create the Systems Thinker agent"""
        agent = Agent(
            role='Senior Systems Thinker and Complexity Navigator',
            goal='Analyze complex systems holistically and identify patterns',
            backstory='Expert systems thinker with deep understanding of complex systems',
            tools=self._create_tools("systems_thinking"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent
    
    def create_data_analyst(self) -> Agent:
        """Create the Data Analyst agent"""
        agent = Agent(
            role='Expert Data Analyst and CSV Processing Specialist',
            goal='Analyze structured data and share insights abundantly',
            backstory='Expert in data analysis with Nature\'s Way principles',
            tools=self._create_tools("data"),
            verbose=True,
            llm=self.llm
        )
        patch_tool_methods(agent)
        remove_competing_delegation_tools(agent)
        return agent

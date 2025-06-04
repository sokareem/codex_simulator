"""CodexSimulator - Intelligent Terminal Assistant with AI-powered command orchestration."""

# Import new tools
from .tools.csv_reader_tool import CSVReaderTool
from .tools.balance_monitor_tool import BalanceMonitorTool  
from .tools.software_architect_tool import SoftwareArchitectTool
from .tools.systems_thinking_tool import SystemsThinkingTool

# Import existing components
from .crew import CodexSimulator
from .tools import *

__version__ = "0.1.0"

__all__ = [
    "CodexSimulator",
    "CSVReaderTool",
    "BalanceMonitorTool", 
    "SoftwareArchitectTool",
    "SystemsThinkingTool",
]

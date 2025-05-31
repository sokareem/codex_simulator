#!/usr/bin/env python

# --- BEGIN ABSOLUTE MINIMAL IMPORTS FOR sys.path MODIFICATION ---
import sys
import pathlib
import os
import traceback
import asyncio
# --- END ABSOLUTE MINIMAL IMPORTS FOR sys.path MODIFICATION ---

# --- BEGIN sys.path MODIFICATION ---
# This section ensures that the project's 'src' directory is in sys.path.
# It MUST be executed before any project-specific imports or imports of
# libraries like CrewAI that might have complex import-time behaviors.

# Get the absolute path of the directory containing the current file (main.py)
# e.g., /Users/sinmi/Projects/codex_simulator/src/codex_simulator
_main_py_file_path = pathlib.Path(__file__).resolve()
_codex_simulator_module_dir = _main_py_file_path.parent

# Navigate up to the 'src' directory
# e.g., /Users/sinmi/Projects/codex_simulator/src
_src_dir = _codex_simulator_module_dir.parent

# Add the 'src' directory to the beginning of sys.path if it's not already there.
# This makes 'codex_simulator' and its submodules importable as top-level packages.
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
if str(_codex_simulator_module_dir) not in sys.path: # Also add the module dir itself for relative imports if needed
    sys.path.insert(0, str(_codex_simulator_module_dir))

# Clean up temporary variables from global scope to avoid polluting the global namespace
del _main_py_file_path, _codex_simulator_module_dir, _src_dir
# --- END sys.path MODIFICATION ---

# Standard library imports
import warnings
import argparse
from datetime import datetime

# Load environment variables from .env file
try:
    import dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False

# Get the project root and load .env
if dotenv_available:
    project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
    dotenv.load_dotenv(project_root / ".env")

# Project-specific imports
try:
    from codex_simulator.crew import CodexSimulator
    from codex_simulator.utils.delegation_fix import apply_delegation_fix
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install -e .")
    sys.exit(1)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from typing import Dict, List, Any, Optional, Union

# Import CrewAI components with error handling
try:
    from crewai import Agent, Task, Crew, Process
    # Try to import Flow components, but handle gracefully if not available
    try:
        from crewai.flow.flow import listen, or_
        FLOW_AVAILABLE = True
    except ImportError:
        print("⚠️ CrewAI Flow not available - using crew-only mode")
        FLOW_AVAILABLE = False
except ImportError as e:
    print(f"❌ CrewAI import error: {e}")
    print("Please install CrewAI: pip install 'crewai[tools]>=0.120.1,<1.0.0'")
    sys.exit(1)

# Add MCP imports with error handling
try:
    from codex_simulator.mcp import MCPClient, MCPConnectionConfig, create_mcp_client
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP components not available")
    MCP_AVAILABLE = False

# --- BEGIN PROJECT IMPORTS ---
# These are imports from within the codex_simulator project.
try:
    from codex_simulator.crew import CodexSimulatorCrew
    from codex_simulator.config.config import load_config
    from codex_simulator.flows.terminal_assistant_flow import TerminalAssistantFlow
    from codex_simulator.mcp.server import run_mcp_server # MCP Server
    from codex_simulator.terminal.claude_style_repl import run_claude_style_terminal # New REPL
    CREW_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing CodexSimulator components: {e}")
    print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"   sys.path: {sys.path}")
    print(f"   Current working directory: {os.getcwd()}")
    print("\n   This might be due to a missing __init__.py in a directory or incorrect PYTHONPATH.")
    print("   Attempting to run will likely fail. Please check your environment and imports.")
    CREW_AVAILABLE = False
    # Define dummy functions if imports fail, so argparsing can still be set up
    class CodexSimulatorCrew: pass
    class TerminalAssistantFlow: pass
    def run_mcp_server(): print("MCP Server components not loaded.")
    def run_claude_style_terminal(): print("Claude-style REPL components not loaded.")
# --- END PROJECT IMPORTS ---

def run():
    """
    Run the crew.
    """
    # This function call is now a no-op but we keep it for compatibility
    apply_delegation_fix()
    
    parser = argparse.ArgumentParser(description='Codex Simulator')
    parser.add_argument('--mode', choices=['report', 'terminal'], default='terminal', 
                        help='Mode to run (report or terminal)')
    parser.add_argument('--no-warning', action='store_true', 
                        help='Disable safety warning for terminal mode')
    parser.add_argument('--topic', default='AI LLMs', 
                        help='Topic for the report mode')
    args = parser.parse_args()
    
    if args.mode == 'terminal':
        # Removed show_warning argument as it's not accepted
        run_terminal_assistant_with_flows() 
    else:
        run_report(topic=args.topic)
        
def run_report(topic='AI LLMs'):
    """Run the crew for report generation"""
    inputs = {
        'topic': topic,
        'current_year': datetime.now().year
    }
    try:
        crew = CodexSimulator().create_report_crew()
        return crew.kickoff(inputs=inputs)
    except Exception as e:
        return f"Error generating report: {e}"

def run_terminal_assistant(show_warning=True):
    """Run terminal assistant in crew-only mode"""
    if show_warning:
        print("🔧 Running terminal assistant in crew-only mode")
    
    try:
        simulator = CodexSimulator()
        
        print("✅ CodexSimulator initialized successfully")
        print("Type 'help' for available commands or 'exit' to quit")
        
        while True:
            try:
                command = input("\n🔹 Enter command: ").strip()
                if command.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                if command:
                    response = simulator.terminal_assistant(command)
                    print(f"\n📄 Response:\n{response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize terminal assistant: {e}")
        return

async def run_terminal_assistant_with_flows_async():
    """Run terminal assistant with flows (async version)"""
    if not FLOW_AVAILABLE:
        print("⚠️ Flow not available, falling back to crew-only mode")
        return run_terminal_assistant(show_warning=False)
    
    try:
        simulator = CodexSimulator(use_mcp=MCP_AVAILABLE)
        print("✅ CodexSimulator with flows initialized successfully")
        print("Type 'help' for available commands or 'exit' to quit")
        
        while True:
            try:
                command = input("\n🔹 Enter command: ").strip()
                if command.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                if command:
                    response = await simulator.terminal_assistant(command)
                    print(f"\n📄 Response:\n{response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize terminal assistant with flows: {e}")
        print("Falling back to crew-only mode...")
        run_terminal_assistant(show_warning=False)

def run_terminal_assistant_with_flows():
    """Run terminal assistant with flows (sync wrapper)"""
    import asyncio
    try:
        asyncio.run(run_terminal_assistant_with_flows_async())
    except Exception as e:
        print(f"❌ Flow execution failed: {e}")
        print("Falling back to crew-only mode...")
        run_terminal_assistant(show_warning=False)

def run_hybrid_mode():
    """Run in hybrid mode (crew + MCP when available)"""
    print("🚀 Starting hybrid mode...")
    if MCP_AVAILABLE:
        print("✅ MCP integration available")
    else:
        print("⚠️ MCP not available, using crew-only mode")
    
    run_terminal_assistant_with_flows()

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        CodexSimulator().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CodexSimulator().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        CodexSimulator().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_mcp_server_standalone():
    """Run standalone MCP server for development"""
    from .mcp.server import run_mcp_server
    
    print("🚀 Starting standalone MCP server...")
    
    # Test tool imports before proceeding
    tools = {}
    
    try:
        from .tools.safe_directory_tool import SafeDirectoryTool
        safe_dir_tool = SafeDirectoryTool()
        tools["safe_directory_tool"] = safe_dir_tool._run
        print("✅ SafeDirectoryTool loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load SafeDirectoryTool: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        from .tools.safe_file_read_tool import SafeFileReadTool
        tools["safe_file_read_tool"] = SafeFileReadTool()._run
        print("✅ SafeFileReadTool loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load SafeFileReadTool: {e}")
    
    try:
        from .tools.safe_file_write_tool import SafeFileWriteTool
        tools["safe_file_write_tool"] = SafeFileWriteTool()._run
        print("✅ SafeFileWriteTool loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load SafeFileWriteTool: {e}")
    
    try:
        from .tools.safe_shell_tool import SafeShellTool
        tools["safe_shell_tool"] = SafeShellTool()._run
        print("✅ SafeShellTool loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load SafeShellTool: {e}")
    
    # Continue with other tools...
    try:
        from .tools.serp_api_tool import SerpAPITool
        tools["serp_api_tool"] = SerpAPITool()._run
        print("✅ SerpAPITool loaded successfully")
    except Exception as e:
        print(f"⚠️ SerpAPITool not available: {e}")
    
    try:
        from .tools.website_tool import WebsiteTool
        tools["website_tool"] = WebsiteTool()._run
        print("✅ WebsiteTool loaded successfully")
    except Exception as e:
        print(f"⚠️ WebsiteTool not available: {e}")
    
    try:
        from .tools.pdf_reader_tool import PDFReaderTool
        tools["pdf_reader_tool"] = PDFReaderTool()._run
        print("✅ PDFReaderTool loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load PDFReaderTool: {e}")
    
    # Add new tools
    try:
        from .tools.new_tools import (
            EnvironmentVariableTool, StaticCodeAnalysisTool, GitManagementTool,
            NetworkDiagnosticTool, PlottingTool, SystemMonitoringTool
        )
        tools["environment_variable_tool"] = EnvironmentVariableTool()._run
        tools["static_code_analysis_tool"] = StaticCodeAnalysisTool()._run
        tools["git_management_tool"] = GitManagementTool()._run
        tools["network_diagnostic_tool"] = NetworkDiagnosticTool()._run
        tools["plotting_tool"] = PlottingTool()._run
        tools["system_monitoring_tool"] = SystemMonitoringTool()._run
        print("✅ New tools loaded successfully")
    except Exception as e:
        print(f"⚠️ Some new tools not available: {e}")
    
    print(f"📊 Total tools loaded: {len(tools)}")
    
    if not tools:
        print("❌ No tools could be loaded. Cannot start MCP server.")
        return
    
    # Run server with registered tools
    asyncio.run(run_mcp_server(
        host="localhost",
        port=8000,
        tools=tools
    ))

def run_claude_repl_entrypoint():
    """Entry point for the Claude-style REPL."""
    if not CREW_AVAILABLE:
        print("❌ Cannot start Claude-style REPL due to import errors. Please check your setup.")
        return
    print("🚀 Starting Claude Code-style Terminal Assistant (Powered by Gemini)...")
    try:
        asyncio.run(run_claude_style_terminal())
    except KeyboardInterrupt:
        print("\n👋 Exiting Claude-style REPL...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred in Claude-style REPL: {e}")
        if "--verbose" in sys.argv or os.environ.get("CODEX_VERBOSE") == "true":
            import traceback
            traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="CodexSimulator: AI Agent Crew Orchestration")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Default crew run command
    parser_run = subparsers.add_parser('run', help='Run the default CodexSimulator crew')
    parser_run.set_defaults(func=run_crew_default)

    # Terminal assistant command
    parser_terminal = subparsers.add_parser('terminal', help='Run the terminal assistant (deprecated, use terminal-flows)')
    parser_terminal.set_defaults(func=run_terminal_assistant_with_flows)

    # Terminal assistant with flows command
    parser_terminal_flows = subparsers.add_parser('terminal-flows', help='Run the terminal assistant with intelligent flows')
    parser_terminal_flows.set_defaults(func=run_terminal_assistant_with_flows)
    
    # Hybrid mode command
    parser_hybrid = subparsers.add_parser('hybrid', help='Run terminal assistant in hybrid mode with complexity assessment')
    parser_hybrid.set_defaults(func=run_hybrid_mode)

    # MCP server command
    parser_mcp = subparsers.add_parser('mcp-server', help='Run the MCP server')
    parser_mcp.add_argument('--host', type=str, default="0.0.0.0", help='Host for MCP server')
    parser_mcp.add_argument('--port', type=int, default=8000, help='Port for MCP server')
    parser_mcp.set_defaults(func=lambda args_ns: run_mcp_server_standalone(host=args_ns.host, port=args_ns.port))

    # New Claude-style REPL command
    parser_claude_repl = subparsers.add_parser('claude-repl', help='Run the Claude Code-style terminal assistant')
    parser_claude_repl.set_defaults(func=lambda: run_claude_repl_entrypoint())

    args = parser.parse_args()

    if hasattr(args, 'func'):
        if args.command == 'mcp-server':
            args.func(args)
        else:
            args.func()
    else:
        # Default action if no command is provided: run claude-repl instead of terminal-flows
        print("No command specified, defaulting to 'claude-repl'. Use --help for options.")
        run_claude_repl_entrypoint()

def terminal_assistant():
    """Run the terminal assistant with flow support"""
    run_terminal_assistant_with_flows()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp-server":
        run_mcp_server_standalone()
    else:
        run_terminal_assistant_with_flows()

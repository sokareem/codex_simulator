#!/usr/bin/env python
import sys
import os
import warnings
import argparse
import traceback
from datetime import datetime

# Fix import issue for direct execution
if __name__ == "__main__" and __package__ is None:
    # Get the absolute path of the current file (main.py)
    current_file_path = os.path.abspath(__file__)
    # Navigate up to the project root (codex_simulator/)
    # main.py is in src/codex_simulator/main.py
    # current_file_path -> .../codex_simulator/src/codex_simulator/main.py
    # os.path.dirname(current_file_path) -> .../codex_simulator/src/codex_simulator
    # os.path.dirname(os.path.dirname(current_file_path)) -> .../codex_simulator/src
    # os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))) -> .../codex_simulator (project root)
    project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    sys.path.insert(0, project_root_dir)
    
    # Now use absolute imports from the project root
    from src.codex_simulator.crew import CodexSimulator
    from src.codex_simulator.utils.delegation_fix import apply_delegation_fix
else:
    from .crew import CodexSimulator
    from .utils.delegation_fix import apply_delegation_fix

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

import asyncio
from typing import Dict, List, Any, Optional, Union

from crewai import Agent, Task, Crew, Process, Flow
from crewai.flow.flow import listen, or_

# Add MCP imports
from .mcp import MCPClient, MCPConnectionConfig, create_mcp_client

# Try to import enhanced UI components with graceful fallback
try:
    from .utils.terminal_ui import terminal_ui
    TERMINAL_UI_AVAILABLE = True
except ImportError as e:
    TERMINAL_UI_AVAILABLE = False
    print(f"⚠️  Enhanced terminal UI not available: {e}")
    print("💡 Run 'python install_enhanced_deps.py' to enable enhanced features")

# Add Nature UI imports with graceful fallback
try:
    from .utils.nature_integration import (
        NatureUIIntegration, 
        start_nature_session,
        get_nature_prompt,
        show_nature_response,
        end_nature_session,
        create_nature_command_handler,
        show_nature_error,
        show_nature_progress
    )
    NATURE_UI_AVAILABLE = True
except ImportError as e:
    NATURE_UI_AVAILABLE = False
    print(f"⚠️  Nature UI not available: {e}")

try:
    from .utils.performance_monitor import performance_monitor
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError as e:
    PERFORMANCE_MONITOR_AVAILABLE = False
    print(f"⚠️  Performance monitoring not available: {e}")

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
    """Run the standard report generation crew"""
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year),
        # Add dummy values for terminal-specific template variables to prevent errors
        'user_command': 'report_generation',
        'cwd': os.getcwd(),
        'file_request': 'none',
        'code_snippet': 'none',
        'search_query': f'Information about {topic}',
        'command': f'Generate report about {topic}'
    }
    
    try:
        print(f"Running report generation on topic: {topic}")
        # Create a specific crew instance for report generation
        simulator = CodexSimulator()
        # Use only the necessary agents for report generation
        report_crew = simulator.create_report_crew()
        report_crew.kickoff(inputs=inputs)
        print(f"Report completed! See report.md for results.")
    except Exception as e:
        print(f"Error running report: {str(e)}")
        if os.environ.get("DEBUG") == "1":
            traceback.print_exc()
        print("\nTrying run_direct_py312.py might be more reliable for now.")

def run_terminal_assistant(show_warning=True):
    """Run the terminal assistant in interactive mode"""
    crew = CodexSimulator()
    
    if show_warning:
        print("=" * 80)
        print("CLAUDE CODE TERMINAL ASSISTANT - SAFETY WARNING")
        print("=" * 80)
        print("This assistant can execute commands on your system. While it has safety measures,")
        print("you should review any commands before allowing them to execute.")
        print("The assistant will only run in the current directory and subdirectories.")
        print("Type 'exit' or 'quit' to exit the assistant.")
        print("=" * 80)
    
    print("Claude Code Terminal Assistant initialized.")
    print(f"Current directory: {os.getcwd()}")
    print("How can I help you today?")
    
    try:
        while True:
            command = input("\n> ")
            if command.lower() in ['exit', 'quit']:
                print("Exiting Claude Code Terminal Assistant. Goodbye!")
                break
                
            result = crew.terminal_assistant(command)
            print(f"\n{result}")
    except KeyboardInterrupt:
        print("\nExiting Claude Code Terminal Assistant. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_terminal_assistant_with_flows():
    """Synchronous wrapper for terminal assistant - fallback to sync mode immediately."""
    try:
        # Skip async entirely and go straight to sync mode
        print("🚀 Starting CodexSimulator (Synchronous Mode)...")
        run_terminal_assistant_simple()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("🔄 Trying basic fallback...")
        run_terminal_assistant_basic_fallback()

def run_terminal_assistant_simple():
    """Simple synchronous terminal assistant with Nature UI integration."""
    print("🚀 Starting CodexSimulator (Simple Mode)...")
    
    try:
        global NATURE_UI_AVAILABLE
        assistant = CodexSimulator()
        
        # Initialize Nature UI session if available
        nature_session = None
        nature_command_handler = None
        
        if NATURE_UI_AVAILABLE:
            try:
                nature_session = start_nature_session("Sinmi", "general")
                nature_command_handler = create_nature_command_handler(nature_session)
                print("🌿 Nature UI initialized successfully!")
            except Exception as e:
                print(f"⚠️  Nature UI initialization failed: {e}")
                NATURE_UI_AVAILABLE = False
        
        # Try enhanced UI with fallback
        ui_available = TERMINAL_UI_AVAILABLE
        if ui_available:
            terminal_ui.clear_screen()
            terminal_ui.print_welcome()
        else:
            print("\n" + "=" * 60)
            print("CodeX Simulator Terminal Assistant")
            print("Simple Mode - Basic terminal interaction") 
            print("=" * 60)
            print()
        
        print("💻 Enter command (or 'quit' to exit):")
        
        while True:
            try:
                # Use Nature UI prompt if available, otherwise fallback to terminal UI
                if NATURE_UI_AVAILABLE:
                    user_input = input(get_nature_prompt())
                elif ui_available:
                    user_input = terminal_ui.get_user_input("❯ ")
                else:
                    user_input = input("❯ ")
                
                if not user_input.strip():
                    continue
                    
                # Handle special Nature UI commands first
                if NATURE_UI_AVAILABLE and nature_command_handler:
                    if nature_command_handler.handle_special_commands(user_input):
                        continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    if NATURE_UI_AVAILABLE:
                        end_nature_session()
                    elif ui_available:
                        terminal_ui.print_system_message("Goodbye! 👋", "info")
                    else:
                        print("👋 Goodbye!")
                    break
                    
                if user_input.lower() == 'clear':
                    if NATURE_UI_AVAILABLE:
                        # Use Nature UI's intentional clearing
                        nature_session.nature_ui.clear_with_intention()
                    elif ui_available:
                        terminal_ui.clear_screen()
                    else:
                        os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                # Show natural progress for processing
                if NATURE_UI_AVAILABLE:
                    show_nature_progress("Processing your request naturally...", 1.0, "seasonal")
                else:
                    print("⏳ Processing...")
                
                # Use the synchronous method
                response = assistant.terminal_assistant_sync(user_input)
                
                # Display response with Nature UI if available
                if NATURE_UI_AVAILABLE:
                    show_nature_response(response, collaborative=True, include_wisdom=True)
                elif ui_available:
                    terminal_ui.print_ai_response(response)
                else:
                    print(f"\n🤖 AI Response:\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n⚠️  Use 'exit' to quit gracefully")
                continue
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                if NATURE_UI_AVAILABLE:
                    show_nature_error(error_msg, collaborative=True)
                elif ui_available:
                    terminal_ui.print_system_message(error_msg, "error")
                else:
                    print(error_msg)
                continue
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("🔄 Trying basic fallback...")
        run_terminal_assistant_basic_fallback()

def run_terminal_assistant_basic_fallback():
    """Most basic fallback terminal assistant."""
    print("🚀 Starting CodexSimulator (Basic Fallback Mode)...")
    print("This is a minimal mode with basic functionality.")
    print()
    
    try:
        while True:
            try:
                user_input = input("Basic❯ ")
                
                if not user_input.strip():
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                    
                if user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                if user_input.lower() in ['help', 'commands']:
                    print("""
Basic Commands Available:
• ls - list files
• pwd - current directory
• cat <file> - show file contents
• help - show this help
• exit/quit - exit the assistant
                    """)
                    continue
                
                # Handle very basic commands directly
                if user_input.strip() == 'ls':
                    try:
                        files = os.listdir(os.getcwd())
                        for f in files:
                            print(f"📁 {f}" if os.path.isdir(f) else f"📄 {f}")
                    except Exception as e:
                        print(f"Error: {e}")
                elif user_input.strip() == 'pwd':
                    print(f"Current directory: {os.getcwd()}")
                else:
                    print("🤖 This is basic fallback mode. Only simple commands (ls, pwd, help) are available.")
                    print("For full functionality, please fix the installation issues.")
                
            except KeyboardInterrupt:
                print("\n⚠️  Use 'exit' to quit gracefully")
                continue
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
                
    except Exception as e:
        print(f"❌ Fatal error in fallback: {e}")

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
    from .tools import (
        SafeDirectoryTool, SafeFileReadTool, SafeFileWriteTool,
        SafeShellTool, SerpAPITool, WebsiteTool
    )
    from .tools.pdf_reader_tool import PDFReaderTool # Added import
    from .tools.translation_tool import TranslationTool # Added import
    
    print("🚀 Starting standalone MCP server...")
    
    # Create tool instances for registration
    tools = {
        "safe_directory_tool": SafeDirectoryTool()._run,
        "safe_file_read_tool": SafeFileReadTool()._run,
        "safe_file_write_tool": SafeFileWriteTool()._run,
        "safe_shell_tool": SafeShellTool()._run,
        "serp_api_tool": SerpAPITool()._run,
        "website_tool": WebsiteTool()._run,
        "pdf_reader_tool": PDFReaderTool()._run, # Added PDFReaderTool
        "translation_tool": TranslationTool()._run # Added TranslationTool
    }
    
    # Run server with registered tools
    asyncio.run(run_mcp_server(
        host="localhost",
        port=8000,
        tools=tools
    ))

def terminal_assistant():
    """Run the terminal assistant with flow support"""
    run_terminal_assistant_with_flows()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp-server":
        run_mcp_server_standalone()
    else:
        run_terminal_assistant_with_flows()

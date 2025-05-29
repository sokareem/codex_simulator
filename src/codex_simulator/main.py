#!/usr/bin/env python
import sys
import os
import warnings
import argparse
import traceback
from datetime import datetime

from .crew import CodexSimulator
# Keep the import but we won't use it actively
from .utils.delegation_fix import apply_delegation_fix

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

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
        run_terminal_assistant_with_flows(show_warning=not args.no_warning)
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

def run_terminal_assistant_with_flows(show_warning=True):
    """Run terminal assistant with flow orchestration"""
    if show_warning:
        print("🚀 Starting CodexSimulator with Flow orchestration...")
        print("⚠️  This assistant can execute code and modify files. Use with caution.")
        print("✨ Type 'help' for available commands or 'quit' to exit.")
    
    # Check Python environment
    print(f"🔍 Checking Python {sys.version_info.major}.{sys.version_info.minor} environment...")
    if sys.version_info.major == 3 and sys.version_info.minor >= 10:
        print(f"✅ Running in Python {sys.version_info.major}.{sys.version_info.minor} environment")
    else:
        print(f"⚠️ Detected Python {sys.version_info.major}.{sys.version_info.minor}. Recommended: Python 3.10+")
    
    simulator = CodexSimulator()
    simulator.flow_enabled = True
    
    while True:
        try:
            command = input("\n💻 Enter command (or 'quit' to exit): ").strip()
            if command.lower() in ['quit', 'exit']:
                break
            
            result = simulator.terminal_assistant(command)
            
            if result.startswith("CLARIFICATION_REQUEST:"):
                clarification_question = result.replace("CLARIFICATION_REQUEST:", "", 1).strip()
                print(f"\n🤔 Assistant needs clarification: {clarification_question}")
                print("   Please rephrase your command or provide more details.")
            else:
                print(f"\n✅ Result:\n{result}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            if os.environ.get("DEBUG") == "1":
                traceback.print_exc()

def run_hybrid_mode():
    """Run with intelligent crew/flow selection"""
    simulator = CodexSimulator()
    
    while True:
        command = input("\n💻 Enter command: ").strip()
        if command.lower() in ['quit', 'exit']:
            break
        
        # Intelligent selection based on command complexity
        complexity_score = simulator._assess_command_complexity(command)
        
        if complexity_score >= 7:
            print("🔄 Using Flow orchestration for complex command...")
            simulator.flow_enabled = True
        else:
            print("⚡ Using direct Crew execution for simple command...")
            simulator.flow_enabled = False
        
        result = simulator.terminal_assistant(command)
        print(f"\n✅ {result}")

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

def terminal_assistant():
    """Run the terminal assistant with flow support"""
    run_terminal_assistant_with_flows()

if __name__ == "__main__":
    terminal_assistant()

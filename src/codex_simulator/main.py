#!/usr/bin/env python
import sys
import os
import warnings
import argparse
from datetime import datetime

from codex_simulator.crew import CodexSimulator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    parser = argparse.ArgumentParser(description='Codex Simulator')
    parser.add_argument('--mode', choices=['report', 'terminal'], default='report', 
                        help='Mode to run (report or terminal)')
    parser.add_argument('--no-warning', action='store_true', 
                        help='Disable safety warning for terminal mode')
    parser.add_argument('--topic', default='AI LLMs', 
                        help='Topic for the report mode')
    args = parser.parse_args()
    
    if args.mode == 'terminal':
        run_terminal_assistant(show_warning=not args.no_warning)
    else:
        run_report(topic=args.topic)
        
def run_report(topic='AI LLMs'):
    """Run the standard report generation crew"""
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year)
    }
    
    try:
        print(f"Running report generation on topic: {topic}")
        CodexSimulator().crew().kickoff(inputs=inputs)
        print(f"Report completed! See report.md for results.")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

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

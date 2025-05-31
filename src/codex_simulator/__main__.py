"""
Entry point for running codex_simulator as a module.
Usage: python -m codex_simulator <command>
"""
import sys
import os
import pathlib

# Ensure proper path setup before any imports
current_file = pathlib.Path(__file__).resolve()
codex_module_dir = current_file.parent
src_dir = codex_module_dir.parent
project_root = src_dir.parent

# Add paths to ensure imports work
paths_to_add = [str(src_dir), str(codex_module_dir)]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

def main():
    """Main entry point for module execution"""
    try:
        from codex_simulator.main import (
            run, terminal_assistant, run_terminal_assistant_with_flows, 
            run_hybrid_mode, run_claude_repl_entrypoint, run_mcp_server_standalone
        )
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == 'terminal_flows':
                run_terminal_assistant_with_flows()
            elif command == 'hybrid_mode':
                run_hybrid_mode()
            elif command == 'terminal':
                terminal_assistant()
            elif command == 'claude-repl':
                run_claude_repl_entrypoint()
            elif command == 'mcp-server':
                run_mcp_server_standalone()
            else:
                run()
        else:
            # Default to Claude-style REPL for better user experience
            run_claude_repl_entrypoint()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Project root: {project_root}")
        print(f"Source directory: {src_dir}")
        print("\nTrying to run from project directory...")
        
        # Change to project root and try again
        try:
            os.chdir(project_root)
            # Set PYTHONPATH environment variable
            os.environ['PYTHONPATH'] = str(src_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')
            from codex_simulator.main import run_claude_repl_entrypoint
            run_claude_repl_entrypoint()
        except Exception as e2:
            print(f"❌ Failed to import even after path adjustments: {e2}")
            print("\n🔧 Please try one of these solutions:")
            print("1. Install the package in development mode:")
            print("   pip install -e .")
            print("\n2. Run from the project root with PYTHONPATH:")
            print(f"   cd {project_root}")
            print("   PYTHONPATH=src python -m codex_simulator")
            print("\n3. Run the script directly:")
            print("   python src/codex_simulator/main.py claude-repl")

if __name__ == "__main__":
    main()

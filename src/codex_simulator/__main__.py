"""
Entry point for running codex_simulator as a module.
Usage: python -m codex_simulator <command>
"""
import sys
import os

# Add the src directory to Python path for proper module resolution
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    """Main entry point for module execution"""
    try:
        from codex_simulator.main import run, terminal_assistant, run_terminal_assistant_with_flows, run_hybrid_mode
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == 'terminal_flows':
                run_terminal_assistant_with_flows()
            elif command == 'hybrid_mode':
                run_hybrid_mode()
            elif command == 'terminal':
                terminal_assistant()
            else:
                run()
        else:
            run()
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying alternative import method...")
        
        # Alternative import method
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from codex_simulator.main import run_terminal_assistant_with_flows
            run_terminal_assistant_with_flows()
        except Exception as e2:
            print(f"Failed to import: {e2}")
            print("\nPlease try running directly with:")
            print("python src/codex_simulator/main.py")

if __name__ == "__main__":
    main()

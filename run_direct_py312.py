#!/usr/bin/env python
"""
Direct runner for CodexSimulator using Python 3.12 environment.
This ensures we're using the correct Python version.
"""
import sys
import os
import subprocess
from pathlib import Path

def check_python312_environment():
    """Check if we're in the Python 3.12 environment"""
    if sys.version_info.major != 3 or sys.version_info.minor != 12:
        return False
    
    # Check if we're in the right virtual environment
    venv_path = Path(__file__).parent / ".venv312"
    if venv_path.exists():
        current_prefix = Path(sys.prefix)
        expected_prefix = venv_path.resolve()
        return current_prefix == expected_prefix
    return False

def activate_python312_and_run():
    """Activate Python 3.12 environment and run the assistant"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv312"
    
    if not venv_path.exists():
        print("❌ Python 3.12 environment not found!")
        print("Please run: python setup_python312_env.py")
        return False
    
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python"
        activate_script = venv_path / "Scripts" / "activate"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
        activate_script = venv_path / "bin" / "activate"
    
    print("🚀 Starting CodexSimulator with Python 3.12...")
    
    # Run the main application
    try:
        # Set environment variables for the subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root / "src")
        
        # Execute the main script
        subprocess.run([
            str(python_path), 
            "-c", 
            """
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from codex_simulator.main import run_terminal_assistant_with_flows
run_terminal_assistant_with_flows()
"""
        ], env=env)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running CodexSimulator: {e}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🔍 Checking Python 3.12 environment...")
    
    if check_python312_environment():
        print("✅ Running in Python 3.12 environment")
        # Add src to path
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        try:
            from codex_simulator.main import run_terminal_assistant_with_flows
            run_terminal_assistant_with_flows()
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Try running: python setup_python312_env.py")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️  Not in Python 3.12 environment, switching...")
        activate_python312_and_run()

if __name__ == "__main__":
    main()

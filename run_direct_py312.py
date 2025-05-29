#!/usr/bin/env python3
"""
Python 3.12 direct runner for the CodexSimulator terminal assistant.
This bypasses potential Python version and module import issues.
"""
import sys
import os
import subprocess
import platform
import site
from pathlib import Path

def get_python312_path():
    """Try to find Python 3.12 in the virtual environment or system"""
    # Check the current virtual environment first if we're in one
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        if sys.version_info.major == 3 and sys.version_info.minor >= 12:
            return sys.executable
        else:
            venv_path = Path(sys.prefix)
            possible_python_paths = [
                venv_path / "bin" / "python3.12",
                venv_path / "bin" / "python312",
                venv_path / "bin" / "python3"
            ]
            for path in possible_python_paths:
                if path.exists():
                    return str(path)
    
    # Check system paths
    if platform.system() == "Windows":
        return "python"  # Assume 'python' command is available and points to Python 3.12
    else:
        # Try standard Unix paths
        for cmd in ["python3.12", "python312", "python3"]:
            try:
                result = subprocess.run(["which", cmd], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
    
    # Last resort, try the current Python
    return sys.executable

def activate_python312_and_run():
    """Activate Python 3.12 environment and run the assistant"""
    python_path = get_python312_path()
    print(f"🔍 Checking Python 3.12 environment...")
    
    # Verify Python version
    try:
        version_check = subprocess.run([python_path, "--version"], 
                                      capture_output=True, text=True)
        version_str = version_check.stdout.strip()
        print(f"✅ Running in {version_str}")
    except Exception as e:
        print(f"❌ Error checking Python version: {e}")
        return False
    
    # Prepare environment variables
    env = os.environ.copy()
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Run terminal assistant with flow orchestration
    try:
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

if __name__ == "__main__":
    success = activate_python312_and_run()
    if not success:
        print("\nTry these troubleshooting steps:")
        print("1. Make sure Python 3.12 is installed")
        print("2. Run: python -m pip install -e .")
        print("3. Try again: python run_direct_py312.py")
        sys.exit(1)

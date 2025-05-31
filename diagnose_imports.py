#!/usr/bin/env python3
"""
Diagnostic script to check import issues and paths.
"""
import sys
import os
from pathlib import Path

def diagnose():
    print("🔍 CodexSimulator Import Diagnostic")
    print("=" * 50)
    
    # Basic info
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    # Path info
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    print(f"Project root: {project_root}")
    print(f"Source directory: {src_dir}")
    print(f"Source directory exists: {src_dir.exists()}")
    
    # Check important directories
    codex_dir = src_dir / "codex_simulator"
    print(f"CodexSimulator directory: {codex_dir}")
    print(f"CodexSimulator directory exists: {codex_dir.exists()}")
    
    init_file = codex_dir / "__init__.py"
    print(f"__init__.py exists: {init_file.exists()}")
    
    main_file = codex_dir / "main.py"
    print(f"main.py exists: {main_file.exists()}")
    
    # Check virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtual environment: {venv_path}")
    else:
        print("No virtual environment detected")
    
    # Check Python path
    print(f"\nCurrent sys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
    
    # Try adding src to path and importing
    print(f"\n📦 Testing imports...")
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"Added {src_dir} to sys.path")
    
    # Test basic import
    try:
        import codex_simulator
        print("✅ Successfully imported codex_simulator")
        print(f"   Location: {codex_simulator.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import codex_simulator: {e}")
    
    # Test main import
    try:
        from codex_simulator import main
        print("✅ Successfully imported codex_simulator.main")
    except ImportError as e:
        print(f"❌ Failed to import codex_simulator.main: {e}")
    
    # Test terminal import
    try:
        from codex_simulator.terminal.claude_style_repl import run_claude_style_terminal
        print("✅ Successfully imported claude_style_repl")
    except ImportError as e:
        print(f"❌ Failed to import claude_style_repl: {e}")
    
    print("\n🔧 Suggested fixes:")
    print("1. Ensure you're in the project root directory")
    print("2. Activate your virtual environment: source .venv312/bin/activate")
    print("3. Install in development mode: pip install -e .")
    print("4. Try the direct runner: python run_claude_repl.py")

if __name__ == "__main__":
    diagnose()

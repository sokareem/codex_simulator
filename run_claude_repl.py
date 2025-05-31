#!/usr/bin/env python3
"""
Direct runner for Claude Code-style REPL.
This bypasses module import issues by running directly.
"""
import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for running CodexSimulator"""
    # Add src to path
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    print(f"🔧 Setting up environment...")
    print(f"   Project root: {project_root}")
    print(f"   Source directory: {src_dir}")
    
    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return False
    
    # Add to Python path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"   ✅ Added {src_dir} to Python path")
    
    # Set PYTHONPATH for subprocess calls
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = str(src_dir)
    if current_pythonpath:
        new_pythonpath = f"{new_pythonpath}{os.pathsep}{current_pythonpath}"
    
    os.environ['PYTHONPATH'] = new_pythonpath
    print(f"   ✅ Set PYTHONPATH: {new_pythonpath}")
    
    # Change to project root
    os.chdir(project_root)
    print(f"   ✅ Changed working directory to: {project_root}")
    
    return True

def test_critical_imports():
    """Test that critical modules can be imported"""
    critical_modules = [
        "pydantic",
        "google.generativeai", 
        "codex_simulator",
        "codex_simulator.terminal.claude_style_repl"
    ]
    
    print(f"\n🧪 Testing critical imports...")
    
    for module_name in critical_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Claude Code-style Terminal Assistant (Direct Mode)")
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Test imports
    if not test_critical_imports():
        print("\n❌ Critical import test failed")
        print("\n🔧 Please try:")
        print("1. Re-run installation: python install_fixed_deps.py")
        print("2. Check virtual environment: source .venv312/bin/activate")
        print("3. Verify Python version: python --version")
        sys.exit(1)
    
    try:
        import asyncio
        from codex_simulator.terminal.claude_style_repl import run_claude_style_terminal
        
        print("\n✅ All systems ready!")
        print("🎯 Starting Claude Code-style interface...")
        
        asyncio.run(run_claude_style_terminal())
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\n🔧 Fallback options:")
        print("1. Try: python -m codex_simulator claude-repl") 
        print("2. Re-install: python install_fixed_deps.py")
        print("3. Check dependencies: python test_imports_fixed.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

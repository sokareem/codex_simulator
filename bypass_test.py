#!/usr/bin/env python3
"""
Bypass test to check imports without problematic tool classes.
"""
import sys
import os
from pathlib import Path

def setup_paths():
    """Setup Python paths for imports"""
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    return src_dir

def test_core_imports():
    """Test core imports without tools"""
    print("🔍 Testing Core Imports (Bypassing Tool Issues)")
    print("=" * 55)
    
    setup_paths()
    
    # Test basic imports
    tests = [
        ("pydantic", "Pydantic validation"),
        ("google.generativeai", "Google Generative AI"),
        ("crewai", "CrewAI framework"),
    ]
    
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name:25} - {description}")
        except ImportError as e:
            print(f"   ❌ {module_name:25} - {description}: {e}")
            return False
    
    # Test CodexSimulator base module
    try:
        import codex_simulator
        print(f"   ✅ codex_simulator module imported")
        print(f"      Location: {codex_simulator.__file__}")
    except ImportError as e:
        print(f"   ❌ codex_simulator module failed: {e}")
        return False
    
    # Test specific components that should work
    try:
        from codex_simulator.permissions.permission_manager import PermissionManager
        print(f"   ✅ PermissionManager imported")
        
        # Test instantiation
        pm = PermissionManager()
        print(f"   ✅ PermissionManager instantiated")
        
    except Exception as e:
        print(f"   ❌ PermissionManager failed: {e}")
        return False
    
    # Test Claude REPL components
    try:
        from codex_simulator.terminal.claude_style_repl import ClaudeStyleREPL
        print(f"   ✅ ClaudeStyleREPL imported")
        
    except Exception as e:
        print(f"   ❌ ClaudeStyleREPL failed: {e}")
        return False
    
    print("\n🎉 Core imports successful!")
    return True

def test_minimal_repl():
    """Test creating a minimal REPL instance"""
    try:
        from codex_simulator.terminal.claude_style_repl import ClaudeStyleREPL
        
        print("\n🚀 Testing Minimal REPL Creation...")
        repl = ClaudeStyleREPL()
        print("   ✅ REPL instance created successfully")
        
        # Test basic context loading
        repl._load_initial_context()
        print("   ✅ Initial context loaded")
        
        return True
        
    except Exception as e:
        print(f"   ❌ REPL creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_core_imports():
        if test_minimal_repl():
            print("\n🎉 All tests passed! CodexSimulator core is working.")
            print("🚀 Try running: python run_claude_repl.py")
        else:
            print("\n⚠️ Core imports work but REPL has issues.")
    else:
        print("\n❌ Core import tests failed.")

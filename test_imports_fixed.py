#!/usr/bin/env python3
"""
Test script to verify CodexSimulator imports work correctly.
"""
import sys
import os
from pathlib import Path

def test_imports():
    print("🔍 Testing CodexSimulator Import Fix")
    print("=" * 50)
    
    # Get project structure
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    print(f"Project root: {project_root}")
    print(f"Source directory: {src_dir}")
    print(f"Source exists: {src_dir.exists()}")
    
    # Ensure src is in Python path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"✅ Added {src_dir} to sys.path")
    
    # Test critical imports
    imports_to_test = [
        ("pydantic", "Pydantic validation library"),
        ("google.generativeai", "Google AI Generative AI"),
        ("crewai", "CrewAI framework"),
        ("codex_simulator", "CodexSimulator main module"),
        ("codex_simulator.main", "CodexSimulator main module"),
        ("codex_simulator.terminal.claude_style_repl", "Claude-style REPL"),
    ]
    
    print(f"\n📦 Testing imports...")
    failed_imports = []
    
    for import_name, description in imports_to_test:
        try:
            module = __import__(import_name)
            print(f"   ✅ {import_name:40} - {description}")
            
            # For codex_simulator, show the actual file location
            if import_name == "codex_simulator" and hasattr(module, '__file__'):
                print(f"      📁 Location: {module.__file__}")
                
        except ImportError as e:
            print(f"   ❌ {import_name:40} - {description}")
            print(f"      Error: {e}")
            failed_imports.append(import_name)
    
    # Test specific function imports
    print(f"\n🎯 Testing specific function imports...")
    
    try:
        from codex_simulator.main import run_claude_repl_entrypoint
        print("   ✅ run_claude_repl_entrypoint imported successfully")
    except ImportError as e:
        print(f"   ❌ run_claude_repl_entrypoint failed: {e}")
        failed_imports.append("run_claude_repl_entrypoint")
    
    try:
        from codex_simulator.terminal.claude_style_repl import run_claude_style_terminal
        print("   ✅ run_claude_style_terminal imported successfully")
    except ImportError as e:
        print(f"   ❌ run_claude_style_terminal failed: {e}")
        failed_imports.append("run_claude_style_terminal")
    
    # Summary
    print(f"\n📊 Import Test Results:")
    print(f"   Total tests: {len(imports_to_test) + 2}")
    print(f"   Passed: {len(imports_to_test) + 2 - len(failed_imports)}")
    print(f"   Failed: {len(failed_imports)}")
    
    if not failed_imports:
        print("\n🎉 All imports successful! CodexSimulator is ready to use.")
        print("\n🚀 Try running:")
        print("   python run_claude_repl.py")
        print("   python -m codex_simulator claude-repl")
        return True
    else:
        print(f"\n❌ Some imports failed: {', '.join(failed_imports)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure you're in the project root directory")
        print("2. Activate virtual environment: source .venv312/bin/activate")
        print("3. Re-run installation: python install_fixed_deps.py")
        print("4. Try direct mode: python run_claude_repl.py")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

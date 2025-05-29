#!/usr/bin/env python
"""
Test script to verify imports work correctly.
"""
import sys
import os

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)
print(f"Added to Python path: {src_path}")

# Test imports one by one
imports_to_test = [
    ('pydantic', 'pydantic'),
    ('crewai', 'crewai'),
    ('google.generativeai', 'google-generativeai'),
    ('dotenv', 'python-dotenv'),
    ('requests', 'requests'),
    ('bs4', 'beautifulsoup4'),
]

print("\n" + "="*50)
print("TESTING IMPORTS")
print("="*50)

for module_name, package_name in imports_to_test:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name} (v{version})")
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        print(f"   Install with: pip install {package_name}")

print("\n" + "="*50)
print("TESTING CODEX_SIMULATOR IMPORTS")
print("="*50)

try:
    from codex_simulator.main import run_terminal_assistant_with_flows
    print("✅ codex_simulator.main imported successfully")
    print("\n🎉 Ready to run: python run_direct.py")
except ImportError as e:
    print(f"❌ codex_simulator import failed: {e}")
    print("\nThis is likely due to missing dependencies above.")

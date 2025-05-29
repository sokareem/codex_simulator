#!/usr/bin/env python
"""
Debug script to check Python environment and paths.
"""
import sys
import os
import subprocess

print("="*60)
print("PYTHON ENVIRONMENT DEBUG")
print("="*60)

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Virtual env active: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")

if hasattr(sys, 'base_prefix'):
    print(f"Base prefix: {sys.base_prefix}")
    print(f"Prefix: {sys.prefix}")

print(f"Current working directory: {os.getcwd()}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")

print("\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\n" + "="*60)
print("CHECKING PIP AND PACKAGES")
print("="*60)

# Check which pip is being used
try:
    pip_location = subprocess.check_output([sys.executable, "-m", "pip", "--version"], text=True)
    print(f"Pip version and location: {pip_location.strip()}")
except Exception as e:
    print(f"Error checking pip: {e}")

# List installed packages
try:
    packages = subprocess.check_output([sys.executable, "-m", "pip", "list"], text=True)
    print("Installed packages:")
    for line in packages.split('\n')[:10]:  # Show first 10 lines
        if line.strip():
            print(f"  {line}")
    print("  ... (truncated)")
except Exception as e:
    print(f"Error listing packages: {e}")

print("\n" + "="*60)
print("TESTING IMPORTS")
print("="*60)

test_imports = [
    'pydantic',
    'crewai', 
    'google.generativeai',
    'dotenv',
    'requests'
]

for module in test_imports:
    try:
        __import__(module)
        print(f"✅ {module} - OK")
    except ImportError as e:
        print(f"❌ {module} - FAILED: {e}")

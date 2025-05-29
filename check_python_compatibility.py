#!/usr/bin/env python
"""
Check Python version compatibility and suggest solutions.
"""
import sys
import subprocess

def check_python_version():
    """Check if current Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Current Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and 10 <= version.minor <= 12:
        print("✅ Python version is compatible with CrewAI")
        return True
    elif version.major == 3 and version.minor == 13:
        print("⚠️  Python 3.13 detected - CrewAI support is limited")
        print("🔧 Trying to find compatible CrewAI version...")
        return check_crewai_compatibility()
    else:
        print("❌ Python version not supported")
        print("   CrewAI requires Python 3.10-3.12")
        return False

def check_crewai_compatibility():
    """Check if we can install a compatible CrewAI version"""
    try:
        # Try to install an older CrewAI version that might work
        print("🔍 Checking available CrewAI versions...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "index", "versions", "crewai"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("📦 Available CrewAI versions found")
            return True
        else:
            print("❌ Could not check CrewAI versions")
            return False
    except Exception as e:
        print(f"❌ Error checking CrewAI compatibility: {e}")
        return False

def suggest_solutions():
    """Suggest solutions for Python version issues"""
    version = sys.version_info
    
    if version.minor == 13:
        print("\n💡 Suggested solutions for Python 3.13:")
        print("1. Install an older CrewAI version (if available):")
        print("   python -m pip install 'crewai[tools]==0.86.0'")
        print("\n2. Use pyenv to install Python 3.11 or 3.12:")
        print("   pyenv install 3.12.0")
        print("   pyenv local 3.12.0")
        print("   python -m venv .venv")
        print("   source .venv/bin/activate")
        print("\n3. Use conda to create a Python 3.12 environment:")
        print("   conda create -n codex_simulator python=3.12")
        print("   conda activate codex_simulator")
    
    print("\n4. Continue with current setup (experimental):")
    print("   python install_deps_experimental.py")

if __name__ == "__main__":
    print("🔍 Checking Python compatibility for CodexSimulator...")
    
    if not check_python_version():
        suggest_solutions()
        sys.exit(1)
    else:
        print("🎉 Python version is compatible!")

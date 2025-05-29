#!/usr/bin/env python
"""
Environment checker for CodexSimulator
Validates Python version and dependencies
"""
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("❌ Python 3 is required")
        return False
    
    if version.minor < 10:
        print("❌ Python 3.10+ is required")
        return False
    
    if version.minor > 12:
        print("⚠️  Python 3.13+ may have compatibility issues with CrewAI")
        print("💡 Recommended: Use Python 3.12 for best compatibility")
        return "warning"
    
    if version.minor == 12:
        print("✅ Python 3.12 - Optimal version for CrewAI")
        return True
    
    print("✅ Python version compatible")
    return True

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"✅ Virtual environment active: {sys.prefix}")
        return True
    else:
        print("⚠️  No virtual environment detected")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('pydantic', 'pydantic>=2.4.2'),
        ('crewai', 'crewai[tools]>=0.86.0'),
        ('google.generativeai', 'google-generativeai>=0.3.0'),
        ('dotenv', 'python-dotenv>=1.0.0'),
        ('requests', 'requests>=2.28.0'),
        ('bs4', 'beautifulsoup4>=4.12.0')
    ]
    
    missing = []
    for package, install_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing.append(install_name)
    
    return missing

def suggest_fixes(missing_deps, python_ok, venv_ok):
    """Suggest fixes for environment issues"""
    print("\n🔧 Recommended Actions:")
    
    if python_ok == "warning":
        print("1. 🐍 Install Python 3.12:")
        print("   • macOS: brew install python@3.12")
        print("   • conda: conda create -n py312 python=3.12")
        print("   • Then run: python setup_python312_env.py")
    
    if not venv_ok:
        print("2. 📦 Create virtual environment:")
        print("   python -m venv .venv && source .venv/bin/activate")
    
    if missing_deps:
        print("3. 📚 Install missing dependencies:")
        for dep in missing_deps:
            print(f"   pip install {dep}")
    
    print("\n🚀 Quick setup with Python 3.12:")
    print("   python setup_python312_env.py && source activate_py312.sh")

def main():
    """Main checker function"""
    print("🔍 CodexSimulator Environment Check")
    print("=" * 40)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check virtual environment
    venv_ok = check_virtual_environment()
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    print("\n📊 Summary:")
    print(f"Python version: {'✅' if python_ok is True else '⚠️' if python_ok == 'warning' else '❌'}")
    print(f"Virtual environment: {'✅' if venv_ok else '❌'}")
    print(f"Dependencies: {'✅' if not missing_deps else f'❌ {len(missing_deps)} missing'}")
    
    if python_ok is True and venv_ok and not missing_deps:
        print("\n🎉 Environment is ready!")
        print("Run: python run_direct.py")
        return True
    else:
        suggest_fixes(missing_deps, python_ok, venv_ok)
        return False

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Dependency installation script for CodexSimulator.
Ensures all dependencies are installed in the current virtual environment.
"""
import subprocess
import sys
import os

def check_venv():
    """Check if we're in a virtual environment"""
    return (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def check_python_compatibility():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major != 3:
        print("❌ Python 3 is required")
        return False
    
    if version.minor < 10:
        print("❌ Python 3.10+ is required")
        return False
    
    if version.minor > 12:
        print("⚠️  Warning: Python 3.13+ may have compatibility issues")
        print("💡 Consider using Python 3.12 for best compatibility")
        print("Run: python setup_python312_env.py")
        return "warning"
    
    return True

def install_dependencies():
    """Install all required dependencies"""
    if not check_venv():
        print("⚠️  Warning: Not in a virtual environment")
        print("Consider creating one: python -m venv .venv && source .venv/bin/activate")
    
    python_ok = check_python_compatibility()
    if python_ok is False:
        return False
    
    print(f"🐍 Using Python {sys.version}")
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    print("\n🔧 Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        return False
    
    # Install compatible versions based on Python version
    if sys.version_info.minor == 12:
        # Python 3.12 - use latest compatible versions
        dependencies = [
            "pydantic>=2.4.2,<3.0.0",
            "crewai[tools]>=0.86.0,<1.0.0",
            "langchain-google-genai>=0.0.1",
            "google-generativeai>=0.3.0",
            "python-dotenv>=1.0.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.12.0"
        ]
    elif sys.version_info.minor == 13:
        # Python 3.13 - use more conservative versions
        dependencies = [
            "pydantic>=2.4.2,<3.0.0",
            "crewai[tools]==0.86.0",  # Pin specific version
            "langchain-google-genai>=0.0.1",
            "google-generativeai>=0.3.0",
            "python-dotenv>=1.0.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.12.0"
        ]
    else:
        # Other Python versions
        dependencies = [
            "pydantic>=2.4.2",
            "crewai[tools]>=0.86.0",
            "langchain-google-genai>=0.0.1", 
            "google-generativeai>=0.3.0",
            "python-dotenv>=1.0.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.12.0"
        ]
    
    failed_installations = []
    
    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ])
            print(f"✅ Successfully installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            failed_installations.append(dep)
    
    if failed_installations:
        print(f"\n⚠️  Some packages failed to install: {failed_installations}")
        if python_ok == "warning":
            print("\n💡 Try using Python 3.12 for better compatibility:")
            print("   python setup_python312_env.py")
        return False
    
    return True

def verify_installation():
    """Verify that key packages can be imported"""
    print("\n🔍 Verifying installation...")
    
    packages_to_test = [
        'pydantic',
        'crewai',
        'google.generativeai',
        'dotenv',
        'requests',
        'bs4'
    ]
    
    failed_imports = []
    
    for package in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  Some packages failed to import: {failed_imports}")
        return False
    else:
        print("\n🎉 All packages imported successfully!")
        return True

if __name__ == "__main__":
    print("🚀 CodexSimulator Dependency Installer")
    print("=" * 50)
    
    if install_dependencies():
        if verify_installation():
            print("\n✅ Installation complete!")
            print("🚀 You can now run: python run_direct.py")
        else:
            print("\n⚠️  Installation completed with warnings")
            print("💡 Try: python setup_python312_env.py for a clean Python 3.12 setup")
    else:
        print("❌ Installation failed!")
        print("💡 Try: python setup_python312_env.py for Python 3.12 environment")
        sys.exit(1)

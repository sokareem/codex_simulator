#!/usr/bin/env python
"""
Python 3.12 Environment Setup for CodexSimulator
Creates a Python 3.12 virtual environment and installs dependencies.
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_python_version():
    """Check if we're running Python 3.12"""
    version = sys.version_info
    if version.major == 3 and version.minor == 12:
        return True
    return False

def find_python312():
    """Find Python 3.12 executable on the system"""
    possible_commands = [
        'python3.12',
        'python3',
        '/usr/bin/python3.12',
        '/usr/local/bin/python3.12',
        '/opt/homebrew/bin/python3.12',
        '/Users/sinmi/miniconda3/bin/python3.12',
        '/Users/sinmi/miniconda3/envs/py312/bin/python'
    ]
    
    for cmd in possible_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'Python 3.12' in result.stdout:
                print(f"✅ Found Python 3.12: {cmd}")
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def create_python312_venv():
    """Create a Python 3.12 virtual environment"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv312"
    
    # Remove existing venv if it exists
    if venv_path.exists():
        print(f"🗑️  Removing existing environment: {venv_path}")
        shutil.rmtree(venv_path)
    
    # Find Python 3.12
    python312 = find_python312()
    if not python312:
        print("❌ Python 3.12 not found on system!")
        print("\nTo install Python 3.12:")
        print("  • macOS with Homebrew: brew install python@3.12")
        print("  • macOS with conda: conda create -n py312 python=3.12")
        print("  • Linux: sudo apt install python3.12-venv python3.12-dev")
        return False
    
    # Create virtual environment
    print(f"🔨 Creating Python 3.12 virtual environment at {venv_path}")
    try:
        subprocess.check_call([python312, "-m", "venv", str(venv_path)])
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies_312():
    """Install dependencies in Python 3.12 environment"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv312"
    
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix/Linux/macOS
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip first
    print("📦 Upgrading pip...")
    try:
        subprocess.check_call([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to upgrade pip: {e}")
    
    # Install compatible dependencies for Python 3.12
    dependencies = [
        "pydantic>=2.4.2,<3.0.0",
        "crewai[tools]>=0.86.0,<1.0.0",  # More conservative version for Python 3.12
        "langchain-core>=0.1.0,<0.3.0",
        "langchain-google-genai>=0.0.1,<2.0.0",
        "google-generativeai>=0.3.0,<1.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
        "typing-extensions>=4.6.1",
        "annotated-types>=0.6.0",
        "pypdf>=4.0.0",
        "langchain-text-splitters>=0.0.1",
        "matplotlib>=3.5.0",
        "psutil>=5.9.0",
        "GitPython>=3.1.0",
        "bandit>=1.7.0"
    ]
    
    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        try:
            subprocess.check_call([str(pip_path), "install", dep])
            print(f"✅ Successfully installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    # Install the project in development mode
    print("📦 Installing codex_simulator in development mode...")
    try:
        subprocess.check_call([str(pip_path), "install", "-e", "."])
        print("✅ Successfully installed codex_simulator")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to install codex_simulator in dev mode: {e}")
    
    return True

def verify_installation_312():
    """Verify the Python 3.12 installation"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv312"
    
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    print("\n🔍 Verifying installation...")
    
    # Check Python version
    try:
        result = subprocess.run([str(python_path), "--version"], 
                              capture_output=True, text=True)
        print(f"Python version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Failed to check Python version: {e}")
        return False
    
    # Test imports
    test_script = '''
import sys
print(f"Python {sys.version}")

test_imports = [
    "pydantic",
    "crewai", 
    "google.generativeai",
    "dotenv",
    "requests",
    "bs4",
    "matplotlib", # Added
    "psutil",     # Added
    "git",        # Added (GitPython imports as 'git')
    "bandit"      # Added
]

failed = []
for module in test_imports:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
        failed.append(module)

if not failed:
    print("\\n🎉 All imports successful!")
else:
    print(f"\\n⚠️  Failed imports: {failed}")
    sys.exit(1)
'''
    
    try:
        result = subprocess.run([str(python_path), "-c", test_script], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Import verification failed")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ Failed to verify imports: {e}")
        return False

def create_activation_script():
    """Create activation script for the Python 3.12 environment"""
    project_root = Path(__file__).parent
    
    # Create activation script
    activation_script = project_root / "activate_py312.sh"
    
    script_content = f'''#!/bin/bash
# Activation script for Python 3.12 CodexSimulator environment

PROJECT_ROOT="{project_root}"
VENV_PATH="$PROJECT_ROOT/.venv312"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Python 3.12 virtual environment not found!"
    echo "Run: python setup_python312_env.py"
    exit 1
fi

echo "🚀 Activating Python 3.12 CodexSimulator environment..."
source "$VENV_PATH/bin/activate"

echo "✅ Environment activated!"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo ""
echo "Available commands:"
echo "  • python run_direct.py"
echo "  • python -m codex_simulator"
echo "  • python src/codex_simulator/main.py"
echo ""
echo "To deactivate: deactivate"
'''
    
    with open(activation_script, 'w') as f:
        f.write(script_content)
    
    os.chmod(activation_script, 0o755)
    print(f"✅ Created activation script: {activation_script}")

def main():
    """Main setup function"""
    print("🐍 Python 3.12 Environment Setup for CodexSimulator")
    print("=" * 60)
    
    # Check if we're already in Python 3.12
    if check_python_version():
        print("✅ Already running Python 3.12")
    else:
        print(f"⚠️  Currently running Python {sys.version_info.major}.{sys.version_info.minor}")
        print("Will create Python 3.12 virtual environment...")
    
    # Create Python 3.12 virtual environment
    if not create_python312_venv():
        print("❌ Failed to create Python 3.12 environment")
        return False
    
    # Install dependencies
    if not install_dependencies_312():
        print("❌ Failed to install dependencies")
        return False
    
    # Verify installation
    if not verify_installation_312():
        print("❌ Installation verification failed")
        return False
    
    # Create activation script
    create_activation_script()
    
    print("\n🎉 Python 3.12 environment setup complete!")
    print("\nTo use the environment:")
    print("  1. Run: source activate_py312.sh")
    print("  2. Or manually: source .venv312/bin/activate")
    print("  3. Then: python run_direct.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

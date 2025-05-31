#!/usr/bin/env python
"""
Direct runner for the CodexSimulator terminal assistant.
This bypasses module import issues.
"""
import sys
import os

def check_virtual_env():
    """Check if we're in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🏠 Virtual environment: {'Yes' if in_venv else 'No'}")
    
    if not in_venv:
        print("⚠️  WARNING: Not in a virtual environment!")
        print("This might cause import issues.")
        print("\nTo fix this:")
        print("1. Run: source .venv/bin/activate")
        print("2. Or run: chmod +x fix_venv.sh && ./fix_venv.sh")
        print("\nContinuing anyway...")
    
    return in_venv

def install_missing_deps():
    """Try to install missing dependencies"""
    print("\n🔧 Attempting to install missing dependencies...")
    
    import subprocess
    
    try:
        # Try installing pydantic specifically
        print("Installing pydantic...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic>=2.4.2"])
        
        print("Installing other dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_dependencies():
    """Check if critical dependencies are available"""
    missing_deps = []
    
    try:
        import pydantic
        print(f"✅ pydantic {pydantic.__version__} found")
    except ImportError:
        missing_deps.append('pydantic')
        print("❌ pydantic not found")
    
    try:
        import crewai
        print(f"✅ crewai found")
    except ImportError:
        missing_deps.append('crewai')
        print("❌ crewai not found")
    
    try:
        import google.generativeai
        print(f"✅ google-generativeai found")
    except ImportError:
        missing_deps.append('google-generativeai')
        print("❌ google-generativeai not found")
    
    return missing_deps

def main():
    """Run the terminal assistant directly"""
    print("🔍 Checking Python environment...")
    
    # Check virtual environment
    check_virtual_env()
    
    # Add src to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    print(f"📂 Added to Python path: {src_path}")
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {missing_deps}")
        
        # Try to install them
        if install_missing_deps():
            print("🔄 Retrying dependency check...")
            missing_deps = check_dependencies()
        
        if missing_deps:
            print(f"\n❌ Still missing dependencies: {missing_deps}")
            print("\nManual fix steps:")
            print("1. Activate your virtual environment: source .venv/bin/activate")
            print("2. Run: python -m pip install --upgrade pip")
            print("3. Run: python -m pip install pydantic>=2.4.2")
            print("4. Run: python -m pip install -r requirements.txt")
            print("5. Try again: python run_direct.py")
            return
    
    try:
        print("\n🚀 Starting CodexSimulator Terminal Assistant...")
        from codex_simulator.main import run_terminal_assistant_with_flows
        run_terminal_assistant_with_flows()
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nRunning debug script...")
        try:
            exec(open('debug_env.py').read())
        except:
            pass
        print("\nTroubleshooting steps:")
        print("1. Run: python debug_env.py")
        print("2. Run: chmod +x fix_venv.sh && ./fix_venv.sh")
        print("3. Try: python -m codex_simulator")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

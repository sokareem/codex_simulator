#!/usr/bin/env python3
"""
Fixed dependency installation script that resolves conflicts step by step.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_pip_command(cmd, description=""):
    """Run pip command with error handling"""
    print(f"🔧 {description}")
    print(f"   Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")
        return False

def install_dependencies_step_by_step():
    """Install dependencies in a specific order to avoid conflicts"""
    
    print("🚀 Installing CodexSimulator dependencies with conflict resolution")
    print("=" * 60)
    
    # Step 1: Upgrade pip and basic tools
    if not run_pip_command([
        sys.executable, "-m", "pip", "install", "--upgrade", 
        "pip", "setuptools", "wheel"
    ], "Upgrading pip and build tools"):
        return False
    
    # Step 2: Install core typing and validation
    if not run_pip_command([
        sys.executable, "-m", "pip", "install",
        "pydantic>=2.4.2,<2.10.0",
        "typing-extensions>=4.0.0",
    ], "Installing core validation libraries"):
        return False
    
    # Step 3: Pin problematic transitive dependencies first (FIXED PROTOBUF VERSION)
    if not run_pip_command([
        sys.executable, "-m", "pip", "install",
        "protobuf>=4.21.6,<5.0.0",  # Changed to 4.x to match google-ai-generativelanguage
        "jsonschema==4.22.0", 
        "jinja2==3.1.2",
        "packaging==23.2",
        "MarkupSafe>=2.0,<3.0",
    ], "Installing pinned transitive dependencies"):
        return False
    
    # Step 4: Install Google AI dependencies with compatible protobuf
    if not run_pip_command([
        sys.executable, "-m", "pip", "install",
        "google-ai-generativelanguage>=0.4.0,<0.5.0",  # Allow range
        "google-api-core>=2.15.0,<2.20.0",
        "google-generativeai>=0.3.2,<0.4.0",
    ], "Installing Google AI components"):
        return False
    
    # Step 5: Install LangChain components
    if not run_pip_command([
        sys.executable, "-m", "pip", "install", 
        "langchain-core==0.1.52",
        "langchain-google-genai==0.0.9",
    ], "Installing LangChain components"):
        return False
    
    # Step 6: Install essential utilities
    if not run_pip_command([
        sys.executable, "-m", "pip", "install",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0", 
        "beautifulsoup4>=4.12.0",
        "pypdf>=4.0.0,<5.0.0",
        "matplotlib>=3.5.0",
        "psutil>=5.9.0",
        "GitPython>=3.1.0",
        "bandit>=1.7.0",
    ], "Installing utility libraries"):
        return False
    
    # Step 7: Install CrewAI without dependencies to avoid conflicts
    if not run_pip_command([
        sys.executable, "-m", "pip", "install",
        "crewai[tools]>=0.86.0,<0.90.0",
        "--no-deps",
    ], "Installing CrewAI (no-deps mode)"):
        return False
    
    print("\n🎉 All dependencies installed successfully!")
    return True

def install_codex_simulator_without_deps():
    """Install CodexSimulator without its dependency requirements to avoid conflicts"""
    print("\n🔧 Installing CodexSimulator without dependency checks...")
    
    # First try installing without --no-deps
    success = run_pip_command([
        sys.executable, "-m", "pip", "install", "-e", "."
    ], "Installing CodexSimulator in development mode")
    
    if not success:
        print("🔄 Trying with --no-deps fallback...")
        # Create a temporary pyproject.toml without the conflicting dependencies
        backup_pyproject = Path("pyproject.toml.backup")
        original_pyproject = Path("pyproject.toml")
        
        if original_pyproject.exists():
            # Backup original
            import shutil
            shutil.copy2(original_pyproject, backup_pyproject)
            
            # Create minimal pyproject.toml
            minimal_content = '''[project]
name = "codex_simulator"
version = "0.1.0"
description = "codex_simulator using crewAI with Flow orchestration"
authors = [{ name = "Your Name", email = "you@example.com" }]
requires-python = ">=3.10,<=3.13"
dependencies = []

[project.scripts]
codex_simulator = "codex_simulator.main:run"
claude_repl = "codex_simulator.main:run_claude_repl_entrypoint"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
            
            try:
                original_pyproject.write_text(minimal_content)
                
                # Install with minimal dependencies
                success = run_pip_command([
                    sys.executable, "-m", "pip", "install", "-e", ".", "--no-deps"
                ], "Installing CodexSimulator (no-deps mode)")
                
            finally:
                # Restore original pyproject.toml
                if backup_pyproject.exists():
                    shutil.copy2(backup_pyproject, original_pyproject)
                    backup_pyproject.unlink()
    
    return success

def create_pth_file():
    """Create a .pth file to ensure the src directory is in Python path"""
    try:
        import site
        site_packages = site.getsitepackages()[0]
        pth_file = Path(site_packages) / "codex_simulator_src.pth"
        src_path = Path(__file__).parent / "src"
        
        print(f"\n🔧 Creating .pth file for module path...")
        print(f"   Writing to: {pth_file}")
        print(f"   Adding path: {src_path}")
        
        pth_file.write_text(str(src_path) + "\n")
        print("   ✅ .pth file created successfully")
        return True
    except Exception as e:
        print(f"   ⚠️ Could not create .pth file: {e}")
        return False

def verify_installation():
    """Verify that key packages can be imported"""
    print("\n🔍 Verifying installation...")
    
    # Add src to path for testing
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"   📁 Added {src_dir} to Python path for testing")
    
    packages_to_test = [
        "pydantic",
        "crewai", 
        "google.generativeai",
        "langchain_core",
        "langchain_google_genai",
        "codex_simulator",
    ]
    
    all_good = True
    for package in packages_to_test:
        try:
            imported_module = __import__(package)
            print(f"   ✅ {package}")
            
            # Show location for codex_simulator
            if package == "codex_simulator" and hasattr(imported_module, '__file__'):
                print(f"      Location: {imported_module.__file__}")
                
        except ImportError as e:
            print(f"   ❌ {package}: {e}")
            all_good = False
    
    return all_good

def main():
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {script_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected - consider using one")
    
    if install_dependencies_step_by_step():
        if install_codex_simulator_without_deps():
            # Try creating .pth file to ensure module is findable
            create_pth_file()
            
            if verify_installation():
                print("\n🎉 Installation completed successfully!")
                print("🚀 You can now run: python run_claude_repl.py")
                print("📋 Alternative: python -m codex_simulator claude-repl")
                return True
            else:
                print("\n⚠️ Installation completed but some imports failed")
                print("🔧 Try running: python run_claude_repl.py (direct mode)")
                return False
        else:
            print("\n❌ Failed to install CodexSimulator package")
            return False
    else:
        print("\n❌ Installation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Install enhanced dependencies for CodexSimulator"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def find_python_executable():
    """Find the correct Python executable to use"""
    # First, check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    # Check for .venv312 directory
    project_root = Path(__file__).parent
    venv312_python = project_root / ".venv312" / "bin" / "python"
    if venv312_python.exists():
        return str(venv312_python)
    
    # Check for .venv directory
    venv_python = project_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to current Python
    return sys.executable

def install_enhanced_dependencies():
    """Install enhanced dependencies for terminal UI and performance monitoring"""
    python_cmd = find_python_executable()
    
    print(f"🚀 Installing enhanced dependencies using: {python_cmd}")
    print(f"📍 Python version: {platform.python_version()}")
    
    # Enhanced dependencies
    enhanced_packages = [
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0", 
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
        "psutil>=5.9.0"
    ]
    
    failed_packages = []
    
    for package in enhanced_packages:
        print(f"📦 Installing {package}...")
        try:
            result = subprocess.run(
                [python_cmd, "-m", "pip", "install", package], 
                check=True, 
                capture_output=True,
                text=True
            )
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}")
            print(f"   Error: {e.stderr}")
            failed_packages.append(package)
        except Exception as e:
            print(f"❌ Unexpected error installing {package}: {e}")
            failed_packages.append(package)
    
    # Verify installation
    print("\n🔍 Verifying installations...")
    test_imports = {
        "rich": "rich.console",
        "prompt_toolkit": "prompt_toolkit",
        "aiofiles": "aiofiles",
        "aiohttp": "aiohttp",
        "psutil": "psutil"
    }
    
    for package_name, import_name in test_imports.items():
        try:
            result = subprocess.run(
                [python_cmd, "-c", f"import {import_name}; print('OK')"],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ {package_name} import test: OK")
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} import test: FAILED")
            
    if failed_packages:
        print(f"\n⚠️  Some packages failed to install: {', '.join(failed_packages)}")
        print("💡 The system will still work with reduced functionality")
        print("🔧 You can try installing them manually later")
        return False
    else:
        print("\n🎉 All enhanced dependencies installed successfully!")
        print("\nNew features now available:")
        print("• 🎨 Rich terminal formatting and colors")
        print("• 📝 Interactive prompts with history and auto-completion") 
        print("• 📊 Performance monitoring and resource tracking")
        print("• 🛡️  Enhanced shell tool with validation")
        print("• 🖥️  Environment-specific optimizations")
        return True

def main():
    """Main installation function"""
    print("🔧 CodexSimulator Enhanced Dependencies Installer")
    print("=" * 50)
    
    # Show current environment info
    print(f"🐍 Current Python: {sys.executable}")
    print(f"📦 Python version: {platform.python_version()}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    venv_status = "Yes" if (hasattr(sys, 'real_prefix') or 
                           (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)) else "No"
    print(f"🌐 Virtual environment: {venv_status}")
    print()
    
    try:
        success = install_enhanced_dependencies()
        if success:
            print("\n🚀 You can now run: python -m codex_simulator.main")
            print("   Or use: ./start_with_mcp.sh")
        else:
            print("\n⚠️  Installation completed with some issues")
            print("🚀 You can still run the basic version")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

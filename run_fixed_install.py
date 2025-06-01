#!/usr/bin/env python3
"""Fixed installation script for CodexSimulator"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("🚀 CodexSimulator Fixed Installation")
    print("=" * 50)
    
    # Ensure we're in the project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Step 1: Install core dependencies
    core_packages = [
        "pydantic>=2.4.2",
        "crewai[tools]>=0.86.0,<1.0.0", 
        "langchain-google-genai>=0.0.1",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
        "langchain-core>=0.1.0",
        "typing-extensions>=4.6.1",
        "annotated-types>=0.6.0"
    ]
    
    print("📦 Installing core dependencies...")
    for package in core_packages:
        if not run_command(f"{sys.executable} -m pip install '{package}'", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Step 2: Install enhanced dependencies
    enhanced_packages = [
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
        "aiofiles>=23.0.0", 
        "aiohttp>=3.8.0",
        "psutil>=5.9.0",
        "tenacity>=8.0.0",
        "tiktoken>=0.5.0"
    ]
    
    print("\n🎨 Installing enhanced dependencies...")
    for package in enhanced_packages:
        if not run_command(f"{sys.executable} -m pip install '{package}'", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Step 3: Verify installation
    print("\n🔍 Verifying critical imports...")
    critical_imports = [
        ("crewai", "CrewAI"),
        ("google.generativeai", "Google Generative AI"),
        ("langchain_google_genai", "Langchain Google GenAI"),
        ("rich", "Rich terminal formatting"),
        ("dotenv", "Python dotenv")
    ]
    
    all_good = True
    for module, name in critical_imports:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {module}; print('OK')"],
                capture_output=True, text=True, check=True
            )
            print(f"✅ {name}: OK")
        except subprocess.CalledProcessError:
            print(f"❌ {name}: FAILED")
            all_good = False
    
    if all_good:
        print("\n🎉 Installation completed successfully!")
        print("\n🚀 You can now run:")
        print("   python -m codex_simulator.main")
        print("   or")
        print("   python src/codex_simulator/main.py")
    else:
        print("\n⚠️ Some dependencies may have issues, but core functionality should work")
        print("🚀 Try running anyway:")
        print("   python -m codex_simulator.main")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

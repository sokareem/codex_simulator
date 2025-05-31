#!/usr/bin/env python
"""
Experimental dependency installer for Python 3.13.
Attempts to install compatible versions or alternatives.
"""
import subprocess
import sys
import os

def install_experimental_deps():
    """Install dependencies with experimental Python 3.13 support"""
    print("🧪 Experimental Python 3.13 dependency installer")
    print("⚠️  This may not work perfectly with all CrewAI features")
    
    # Try installing an older CrewAI version
    crewai_versions_to_try = [
        "crewai[tools]==0.86.0",
        "crewai[tools]==0.80.0", 
        "crewai[tools]==0.76.0",
        "crewai[tools]==0.70.0"
    ]
    
    crewai_installed = False
    for version in crewai_versions_to_try:
        print(f"\n📦 Trying to install {version}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                version, "--no-deps"  # Skip dependency checking
            ])
            print(f"✅ Successfully installed {version}")
            crewai_installed = True
            break
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {version}")
            continue
    
    if not crewai_installed:
        print("❌ Could not install any CrewAI version")
        return False
    
    # Install remaining dependencies
    remaining_deps = [
        "pydantic>=2.4.2",
        "langchain-google-genai>=0.0.1", 
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
        "langchain-core>=0.1.0",
        "typing-extensions>=4.6.1",
        "annotated-types>=0.6.0"
    ]
    
    for dep in remaining_deps:
        print(f"📦 Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to install {dep}: {e}")
    
    return True

if __name__ == "__main__":
    if install_experimental_deps():
        print("\n🎉 Experimental installation completed!")
        print("🧪 Try running: python run_direct.py")
    else:
        print("\n❌ Experimental installation failed!")
        sys.exit(1)

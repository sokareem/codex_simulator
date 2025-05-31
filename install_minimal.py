#!/usr/bin/env python3
"""
Minimal installation script that installs only what's needed for the Claude REPL.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run command with error handling"""
    print(f"🔧 {description}")
    print(f"   Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    print("🚀 Minimal CodexSimulator Installation")
    print("=" * 40)
    
    # Core dependencies only
    essential_packages = [
        "pydantic>=2.4.2,<2.10.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
        # Use protobuf 4.x for compatibility
        "protobuf>=4.21.6,<5.0.0",
        "google-generativeai>=0.3.2,<0.4.0",
    ]
    
    # Install essential packages
    if not run_command([
        sys.executable, "-m", "pip", "install"
    ] + essential_packages, "Installing essential packages"):
        return False
    
    print("\n✅ Minimal installation complete!")
    print("🚀 You can now run: python run_claude_repl.py")
    
    # Test basic import
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

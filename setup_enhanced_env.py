"""Setup script for enhanced CodexSimulator environment with new dependencies."""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Setup enhanced environment with new dependencies."""
    print("🔧 Setting up enhanced CodexSimulator environment...")
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install enhanced dependencies
    enhanced_packages = [
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0", 
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
        "psutil>=5.9.0"
    ]
    
    print("📦 Installing enhanced dependencies...")
    for package in enhanced_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            
    print("🎉 Enhanced environment setup complete!")
    print("\nNew features available:")
    print("• Rich terminal formatting and colors")
    print("• Interactive prompts with history and auto-completion") 
    print("• Performance monitoring and resource tracking")
    print("• Enhanced shell tool with validation")
    print("• Environment-specific optimizations")

if __name__ == "__main__":
    main()

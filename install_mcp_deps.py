#!/usr/bin/env python3
"""Install MCP-specific dependencies"""

import subprocess
import sys

def install_mcp_dependencies():
    """Install dependencies required for MCP integration"""
    mcp_deps = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "websockets>=12.0",
        "aiohttp>=3.9.0",
        "pydantic>=2.5.0"
    ]
    
    print("🔧 Installing MCP dependencies...")
    
    for dep in mcp_deps:
        print(f"📦 Installing {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("🎉 All MCP dependencies installed successfully!")
    return True

if __name__ == "__main__":
    success = install_mcp_dependencies()
    sys.exit(0 if success else 1)

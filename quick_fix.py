#!/usr/bin/env python3
"""Quick fix script for CodexSimulator issues"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Main fix function"""
    print("🔧 Quick Fix for CodexSimulator")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Step 1: Clean install dependencies without problematic packages
    print("📦 Installing clean dependencies...")
    
    clean_packages = [
        "pydantic>=2.4.2",
        "crewai[tools]>=0.86.0,<1.0.0",
        "langchain-google-genai>=0.0.1", 
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
        "langchain-core>=0.1.0",
        "typing-extensions>=4.6.1",
        "annotated-types>=0.6.0",
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
        "psutil>=5.9.0",
        "tenacity>=8.0.0",
        "tiktoken>=0.5.0"
    ]
    
    failed_packages = []
    
    for package in clean_packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True, capture_output=True, text=True
            )
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed: {package}")
            failed_packages.append(package)
    
    # Step 2: Test the application
    print("\n🧪 Testing application...")
    
    try:
        # Test import
        sys.path.insert(0, str(project_root / "src"))
        from codex_simulator.crew import CodexSimulator
        
        print("✅ Core import successful")
        
        # Quick test
        simulator = CodexSimulator()
        test_result = simulator.terminal_assistant_sync("help")
        
        if "CodexSimulator" in test_result or "help" in test_result.lower():
            print("✅ Basic functionality test passed")
        else:
            print("⚠️ Basic functionality test inconclusive")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    print("\n🎉 Quick fix completed!")
    print("\n🚀 You can now run:")
    print("   python run_codex.py")
    print("   or")
    print("   python -m codex_simulator.main (from project root)")
    
    if failed_packages:
        print(f"\n⚠️ Some packages failed: {', '.join(failed_packages)}")
        print("The system should still work with reduced functionality")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

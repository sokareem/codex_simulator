#!/usr/bin/env python3
"""Simple launcher script for CodexSimulator"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main launcher function"""
    try:
        # Import and run the simulator
        from codex_simulator.main import run_terminal_assistant_simple
        
        print("🚀 Starting CodexSimulator...")
        run_terminal_assistant_simple()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Trying alternative import method...")
        
        try:
            # Alternative method
            from codex_simulator.crew import CodexSimulator
            
            print("🚀 Starting CodexSimulator (Alternative Mode)...")
            simulator = CodexSimulator()
            
            print("💻 Enter command (or 'quit' to exit):")
            while True:
                try:
                    user_input = input("❯ ")
                    
                    if not user_input.strip():
                        continue
                        
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    
                    print("⏳ Processing...")
                    response = simulator.terminal_assistant_sync(user_input)
                    print(f"\n🤖 AI Response:\n{response}\n")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            print("🔧 Please check your installation and try again")
            return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())

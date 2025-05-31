#!/usr/bin/env python3
"""
Minimal REPL runner that bypasses tool import issues.
"""
import sys
import os
import asyncio
from pathlib import Path

def setup_environment():
    """Setup environment for minimal REPL"""
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    os.chdir(project_root)
    return True

async def run_minimal_claude_repl():
    """Run a minimal version of the Claude REPL"""
    print("🚀 Starting Minimal Claude Code-style Terminal (Bypassing Tool Issues)")
    print("=" * 70)
    
    try:
        # Import minimal components
        from codex_simulator.llms.custom_gemini_llm import CustomGeminiLLM
        from codex_simulator.permissions.permission_manager import PermissionManager
        
        print("✅ Core components imported successfully")
        
        # Initialize basic components
        llm = CustomGeminiLLM()
        permission_manager = PermissionManager()
        
        print("✅ Components initialized")
        print("\n💡 This is a minimal Claude-style interface.")
        print("📝 Type your requests or 'exit' to quit.\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Simple echo for now
                print(f"🤔 You said: {user_input}")
                print("📝 (Minimal mode - full tool integration coming soon)")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start minimal REPL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if setup_environment():
        asyncio.run(run_minimal_claude_repl())
    else:
        print("❌ Environment setup failed")

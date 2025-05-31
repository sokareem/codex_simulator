#!/usr/bin/env python3
"""
Fixed Claude Code-style REPL runner that bypasses all import issues.
This creates a minimal working version that can be expanded later.
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Set up the environment for running"""
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    print(f"🔧 Setting up environment...")
    print(f"   Project root: {project_root}")
    print(f"   Source directory: {src_dir}")
    
    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return False
    
    # Add to Python path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        print(f"   ✅ Added {src_dir} to Python path")
    
    # Change to project root
    os.chdir(project_root)
    print(f"   ✅ Changed working directory to: {project_root}")
    
    return True

class MinimalClaudeREPL:
    """Minimal Claude Code-style REPL that works independently"""
    
    def __init__(self):
        self.running = False
        self.conversation_history = []
        
        # Try to initialize Gemini LLM
        self.llm = None
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.llm = genai.GenerativeModel("gemini-1.5-flash")
                print("✅ Gemini LLM initialized successfully")
            else:
                print("⚠️ No Google API key found (GOOGLE_API_KEY or GEMINI_API_KEY)")
        except ImportError:
            print("⚠️ google-generativeai not available")
        except Exception as e:
            print(f"⚠️ Could not initialize Gemini LLM: {e}")
        
        self._ensure_claude_md_exists()
    
    def _ensure_claude_md_exists(self):
        """Ensure CLAUDE.md exists in current directory"""
        claude_md_path = Path.cwd() / "CLAUDE.md"
        if not claude_md_path.exists():
            initial_content = f"""# Claude Memory File

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Initial Working Directory: {Path.cwd()}

## Project Context
This is a CodexSimulator project with Claude Code-style interface.

## Coding Preferences
- Use descriptive variable names
- Follow project-specific coding standards
- Prioritize code safety and security

## Common Commands
- Use `/help` for available commands
- Use `/memory` to edit this file
- Use `/status` for system information

---
*This file is automatically loaded as context for Claude interactions*
"""
            try:
                claude_md_path.write_text(initial_content, encoding='utf-8')
                print(f"✅ Created CLAUDE.md in {Path.cwd()}")
            except Exception as e:
                print(f"⚠️ Could not create CLAUDE.md: {e}")
    
    async def start_interactive_session(self):
        """Main REPL loop"""
        self.running = True
        
        # Display welcome message
        self._display_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Handle different input types
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif user_input.startswith('/'):
                    await self._handle_slash_command(user_input)
                elif user_input.startswith('#'):
                    await self._handle_memory_shortcut(user_input)
                else:
                    await self._process_natural_language_command(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Use 'exit' or Ctrl+D to quit gracefully")
                continue
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _display_welcome(self):
        """Display welcome message"""
        print("🤖 Claude Code-style Terminal Assistant (Minimal Mode)")
        print(f"📁 Working directory: {Path.cwd()}")
        
        if self.llm:
            print("🧠 Gemini LLM: Available")
        else:
            print("🧠 Gemini LLM: Not available (set GOOGLE_API_KEY)")
        
        if (Path.cwd() / "CLAUDE.md").exists():
            print("📋 Loaded project memory from CLAUDE.md")
        
        print("\n💡 Try: 'help me understand this project' or '/help' for commands")
        print("🎯 Type your request in natural language, or use slash commands\n")
    
    async def _handle_slash_command(self, command: str):
        """Handle basic slash commands"""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            self._show_help()
        elif cmd == '/status':
            self._show_status()
        elif cmd == '/cwd':
            print(f"📁 Current working directory: {Path.cwd()}")
        elif cmd.startswith('/cd '):
            path = command[4:].strip()
            await self._change_directory(path)
        elif cmd == '/memory':
            await self._edit_memory()
        elif cmd == '/clear':
            self.conversation_history.clear()
            print("🧹 Conversation history cleared.")
        else:
            print(f"❓ Unknown command: {command}. Try /help.")
    
    def _show_help(self):
        """Show help information"""
        print("\n🤖 Claude Code-style Terminal Assistant Help:")
        print("-" * 45)
        print("Available slash commands:")
        print("  /help       - Show this help")
        print("  /status     - Show system status")
        print("  /cwd        - Show current directory")
        print("  /cd <path>  - Change directory")
        print("  /memory     - Edit CLAUDE.md")
        print("  /clear      - Clear conversation")
        print("  exit/quit   - Exit the assistant")
        print("\nMemory Shortcut:")
        print("  # <text>    - Add text to CLAUDE.md")
        print("\nNatural Language:")
        print("  Just type your request in plain English!")
        print("-" * 45)
    
    def _show_status(self):
        """Show system status"""
        print("\n📊 System Status:")
        print(f"  Python Version: {sys.version.split()[0]}")
        print(f"  Working Directory: {Path.cwd()}")
        print(f"  Conversation Length: {len(self.conversation_history)} messages")
        print(f"  Gemini LLM: {'Available' if self.llm else 'Not available'}")
        print(f"  CLAUDE.md: {'Exists' if (Path.cwd() / 'CLAUDE.md').exists() else 'Not found'}")
    
    async def _change_directory(self, path: str):
        """Change directory"""
        if not path:
            print("Usage: /cd <directory_path>")
            return
        
        new_dir = Path(path).expanduser()
        try:
            os.chdir(new_dir)
            print(f"📁 Changed working directory to: {Path.cwd()}")
            self._ensure_claude_md_exists()
        except FileNotFoundError:
            print(f"❌ Directory not found: {new_dir}")
        except Exception as e:
            print(f"❌ Failed to change directory: {e}")
    
    async def _edit_memory(self):
        """Edit CLAUDE.md file"""
        claude_md = Path.cwd() / "CLAUDE.md"
        editor = os.environ.get('EDITOR', 'nano')
        
        try:
            import subprocess
            print(f"📝 Opening {claude_md} with {editor}...")
            subprocess.run([editor, str(claude_md)], check=True)
            print(f"✅ Finished editing {claude_md}")
        except FileNotFoundError:
            print(f"❌ Editor '{editor}' not found. Please set your EDITOR environment variable.")
        except Exception as e:
            print(f"❌ Error editing file: {e}")
    
    async def _handle_memory_shortcut(self, memory_input: str):
        """Handle memory shortcuts starting with #"""
        memory_text = memory_input[1:].strip()
        if not memory_text:
            print("💡 Usage: # your memory text here")
            return
        
        claude_md = Path.cwd() / "CLAUDE.md"
        try:
            with claude_md.open("a", encoding="utf-8") as f:
                f.write(f"\n\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{memory_text}\n")
            print(f"💾 Added to memory: {memory_text}")
        except Exception as e:
            print(f"❌ Could not add to memory: {e}")
    
    async def _process_natural_language_command(self, command: str):
        """Process natural language commands"""
        if not self.llm:
            print("❌ Gemini LLM not available. Please set GOOGLE_API_KEY environment variable.")
            print("💡 You can still use slash commands like /help, /status, /memory")
            return
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": command,
            "timestamp": datetime.now()
        })
        
        try:
            print("🤔 Thinking...")
            
            # Build simple context
            context = self._build_context(command)
            
            # Get response from Gemini
            response = self.llm.generate_content(context)
            response_text = response.text
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now()
            })
            
            # Display response
            print(f"\n{response_text}\n")
            
        except Exception as e:
            print(f"❌ Error getting response: {e}")
    
    def _build_context(self, command: str) -> str:
        """Build context for LLM"""
        context_parts = []
        
        # System prompt
        context_parts.append("""You are Claude Code, a helpful coding assistant. You help users with:
- Understanding codebases and projects
- Explaining code and architecture
- Answering programming questions
- Providing coding guidance and best practices

You're currently in a terminal interface. Be concise but helpful.""")
        
        # Add CLAUDE.md content if it exists
        claude_md = Path.cwd() / "CLAUDE.md"
        if claude_md.exists():
            try:
                memory_content = claude_md.read_text(encoding='utf-8')
                context_parts.append(f"## Project Memory:\n{memory_content}")
            except Exception:
                pass
        
        # Add recent conversation
        if self.conversation_history:
            recent = self.conversation_history[-3:]  # Last 3 exchanges
            history_text = []
            for item in recent:
                history_text.append(f"{item['role']}: {item['content']}")
            context_parts.append(f"## Recent Conversation:\n" + "\n".join(history_text))
        
        # Add current request
        context_parts.append(f"## Current Request:\n{command}")
        context_parts.append(f"## Working Directory:\n{Path.cwd()}")
        
        return "\n\n".join(context_parts)

async def main():
    """Main entry point"""
    print("🚀 Starting Fixed Claude Code-style Terminal Assistant")
    
    if not setup_environment():
        print("❌ Environment setup failed")
        return
    
    repl = MinimalClaudeREPL()
    await repl.start_interactive_session()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

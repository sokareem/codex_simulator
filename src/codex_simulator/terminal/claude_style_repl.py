"""
Claude Code-style terminal REPL interface for CodexSimulator.
Provides natural language interaction while preserving existing MCP and tool capabilities.
"""

import asyncio
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import readline

# Import only the components we know work
try:
    from ..permissions.permission_manager import PermissionManager
    PERMISSIONS_AVAILABLE = True
except ImportError:
    PERMISSIONS_AVAILABLE = False
    print("⚠️ Permission manager not available")

try:
    from ..session.session_manager import SessionManager
    SESSIONS_AVAILABLE = True
except ImportError:
    SESSIONS_AVAILABLE = False
    print("⚠️ Session manager not available")

try:
    from ..commands.slash_commands import SlashCommandHandler
    SLASH_COMMANDS_AVAILABLE = True
except ImportError:
    SLASH_COMMANDS_AVAILABLE = False
    print("⚠️ Slash commands not available")

try:
    from ..tools.claude_tools import ClaudeToolAdapter
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    print("⚠️ Tool adapter not available")

try:
    from ..context.claude_context import ClaudeContextManager
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    print("⚠️ Context manager not available")

try:
    from ..llms.custom_gemini_llm import CustomGeminiLLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ Custom Gemini LLM not available")


class ClaudeStyleREPL:
    """
    Claude Code-style REPL interface that integrates with CodexSimulator's
    existing MCP and tool infrastructure while providing intuitive natural language interaction.
    """
    
    def __init__(self, use_mcp: bool = False, mcp_server_url: str = None):
        self.use_mcp = use_mcp
        self.mcp_server_url = mcp_server_url
        
        # Initialize components that are available
        self.session_manager = SessionManager() if SESSIONS_AVAILABLE else None
        self.permission_manager = PermissionManager() if PERMISSIONS_AVAILABLE else None
        self.slash_handler = SlashCommandHandler(self) if SLASH_COMMANDS_AVAILABLE else None
        self.tool_adapter = ClaudeToolAdapter(use_mcp=use_mcp, mcp_server_url=mcp_server_url) if TOOLS_AVAILABLE else None
        self.context_manager = ClaudeContextManager() if CONTEXT_AVAILABLE else None
        
        # Initialize Gemini LLM if available
        self.llm = None
        if LLM_AVAILABLE:
            try:
                self.llm = CustomGeminiLLM()
                print("✅ Gemini LLM initialized successfully")
            except Exception as e:
                print(f"⚠️ Could not initialize Gemini LLM: {e}")
        
        # REPL state
        self.current_session_id = None
        self.conversation_history = []
        self.running = False
        
        # Load initial context if available
        self._load_initial_context()
    
    def _load_initial_context(self):
        """Load CLAUDE.md files and initialize session context"""
        try:
            if self.context_manager:
                self.context_manager.load_project_memory()
                self.context_manager.load_user_memory()
            self._ensure_claude_md_exists()
        except Exception as e:
            print(f"⚠️ Warning: Could not load initial context: {e}")
    
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
- Use `/config` for settings

---
*This file is automatically loaded as context for Claude interactions*
"""
            try:
                claude_md_path.write_text(initial_content, encoding='utf-8')
                print(f"✅ Created CLAUDE.md in {Path.cwd()}")
            except Exception as e:
                print(f"⚠️ Could not create CLAUDE.md: {e}")
    
    async def start_interactive_session(self):
        """Main REPL loop matching Claude Code's interface"""
        self.running = True
        
        if self.session_manager:
            self.current_session_id = self.session_manager.create_new_session()
        
        # Display welcome message
        self._display_welcome()
        
        while self.running:
            try:
                # Get user input with Claude-style prompt
                user_input = await self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Handle different input types
                if user_input.startswith('/'):
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
                if "--verbose" in sys.argv:
                    traceback.print_exc()
    
    def _display_welcome(self):
        """Display Claude Code-style welcome message"""
        print("🤖 Claude Code-style Terminal Assistant (Powered by Gemini)")
        print(f"📁 Working directory: {Path.cwd()}")
        
        if self.use_mcp:
            print(f"🔗 MCP enabled: {self.mcp_server_url}")
        
        # Check for CLAUDE.md
        if (Path.cwd() / "CLAUDE.md").exists():
            print("📋 Loaded project memory from CLAUDE.md")
        
        # Show available components
        components = []
        if self.llm: components.append("LLM")
        if self.session_manager: components.append("Sessions")
        if self.permission_manager: components.append("Permissions")
        if self.tool_adapter: components.append("Tools")
        if self.context_manager: components.append("Context")
        
        if components:
            print(f"🔧 Available components: {', '.join(components)}")
        
        print("\n💡 Try: 'help me understand this project' or '/help' for commands")
        print("🎯 Type your request in natural language, or use slash commands for quick actions\n")
    
    async def _get_user_input(self) -> str:
        """Get user input with Claude-style prompt and multiline support"""
        try:
            # Simple prompt for now - can be enhanced with colors later
            prompt = "> "
            user_input = input(prompt).strip()
            
            # Handle multiline input with backslash continuation
            while user_input.endswith('\\'):
                user_input = user_input[:-1] + '\n'
                continuation = input("  ").strip()
                user_input += continuation
            
            return user_input
            
        except (EOFError, KeyboardInterrupt):
            raise
    
    async def _handle_slash_command(self, command: str):
        """Handle slash commands like Claude Code"""
        if not self.slash_handler:
            print("❌ Slash commands not available")
            return
            
        try:
            await self.slash_handler.execute(command)
        except Exception as e:
            print(f"❌ Slash command error: {e}")
    
    async def _handle_memory_shortcut(self, memory_input: str):
        """Handle memory shortcuts starting with #"""
        memory_text = memory_input[1:].strip()
        if not memory_text:
            print("💡 Usage: # your memory text here")
            return
        
        print(f"💾 Adding to memory: {memory_text}")
        
        if self.context_manager:
            # Prompt for memory location
            print("\nSelect memory location:")
            print("1. Project memory (./CLAUDE.md)")
            print("2. User memory (~/.claude/CLAUDE.md)")
            
            choice = input("Choice (1-2): ").strip()
            
            if choice == "1":
                self.context_manager.add_to_project_memory(memory_text)
                print("✅ Added to project memory")
            elif choice == "2":
                self.context_manager.add_to_user_memory(memory_text)
                print("✅ Added to user memory")
            else:
                print("❌ Invalid choice")
        else:
            # Fallback - add to project CLAUDE.md directly
            claude_md = Path.cwd() / "CLAUDE.md"
            try:
                with claude_md.open("a", encoding="utf-8") as f:
                    f.write(f"\n\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{memory_text}\n")
                print("✅ Added to project memory")
            except Exception as e:
                print(f"❌ Could not add to memory: {e}")
    
    async def _process_natural_language_command(self, command: str):
        """Process natural language commands using Gemini LLM"""
        if not self.llm:
            print("❌ LLM not available. Cannot process natural language commands.")
            print("💡 Try using slash commands like /help, /config, /status")
            return
            
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": command,
                "timestamp": datetime.now()
            })
            
            # Build context for LLM
            context = self._build_llm_context(command)
            
            # Get LLM response
            print("🤔 Thinking...")
            response = await self._get_llm_response(context)
            
            # Process LLM response and execute tools if needed
            await self._execute_llm_response(response, command)
            
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    def _build_llm_context(self, command: str) -> str:
        """Build context for LLM including memory and session state"""
        context_parts = []
        
        # Add system context
        context_parts.append("""You are Claude Code, an agentic coding assistant that operates in a terminal environment. 
You help users with coding tasks through natural language commands.

Key capabilities:
- Read and analyze files and directories
- Edit code and fix bugs
- Execute shell commands (with permission)
- Search through codebases  
- Answer questions about code architecture
- Create and manage files
- Git operations

You have access to these tools:
- Read: Read file contents
- Edit: Make targeted edits to files  
- Write: Create or overwrite files
- Bash: Execute shell commands (requires permission)
- LS: List directory contents
- Grep: Search for patterns in files
- WebFetch: Fetch content from URLs (requires permission)

Always explain what you're doing and ask for permission before making changes.""")
        
        # Add memory context if available
        if self.context_manager:
            memory_context = self.context_manager.get_full_context()
            if memory_context:
                context_parts.append(f"## Memory Context:\n{memory_context}")
        
        # Add recent conversation history
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]  # Last 5 exchanges
            history_text = []
            for item in recent_history:
                history_text.append(f"{item['role']}: {item['content']}")
            context_parts.append(f"## Recent Conversation:\n" + "\n".join(history_text))
        
        # Add current command
        context_parts.append(f"## Current Request:\n{command}")
        
        # Add working directory context
        context_parts.append(f"## Current Working Directory:\n{Path.cwd()}")
        
        return "\n\n".join(context_parts)
    
    async def _get_llm_response(self, context: str) -> str:
        """Get response from Gemini LLM"""
        try:
            # Use your existing CustomGeminiLLM
            response = await asyncio.to_thread(self.llm.invoke, context)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            raise Exception(f"LLM error: {e}")
    
    async def _execute_llm_response(self, response: str, original_command: str):
        """Process LLM response and execute any required tools"""
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now()
        })
        
        # Display response
        print(f"\n{response}")
        
        # Parse response for tool usage (simplified for now)
        # In a full implementation, you'd parse structured tool calls
        await self._parse_and_execute_tools(response, original_command)
        
        # Update session context if available
        if self.session_manager:
            self.session_manager.update_session_context(
                self.current_session_id,
                original_command,
                response
            )
    
    async def _parse_and_execute_tools(self, response: str, original_command: str):
        """Parse LLM response for tool usage and execute with permissions"""
        # This is a simplified implementation
        # In practice, you'd want structured tool calling from the LLM
        
        # Example: If LLM mentions reading a file
        if "let me read" in response.lower() and "file" in response.lower():
            # Extract filename and execute with permission
            # This would be more sophisticated in practice
            pass
        
        print()  # Add spacing after response
    
    def stop(self):
        """Stop the REPL"""
        self.running = False
        if self.current_session_id and self.session_manager:
            self.session_manager.save_session(self.current_session_id)


# Convenience function for backwards compatibility
async def run_claude_style_terminal():
    """Run the Claude-style terminal interface"""
    use_mcp = os.environ.get('USE_MCP', 'false').lower() == 'true'
    mcp_url = os.environ.get('MCP_SERVER_URL', 'http://localhost:8000')
    
    repl = ClaudeStyleREPL(use_mcp=use_mcp, mcp_server_url=mcp_url)
    await repl.start_interactive_session()


if __name__ == "__main__":
    asyncio.run(run_claude_style_terminal())

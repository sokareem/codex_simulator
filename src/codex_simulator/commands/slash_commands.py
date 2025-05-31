"""
Slash command handler for the Claude Code-style REPL.
Implements commands like /help, /config, /memory, etc.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Callable, Awaitable, List

if TYPE_CHECKING:
    from ..terminal.claude_style_repl import ClaudeStyleREPL


class SlashCommandHandler:
    """Handles slash commands for the Claude-style REPL."""
    
    def __init__(self, repl_instance: 'ClaudeStyleREPL'):
        self.repl = repl_instance
        self.commands: Dict[str, Callable[..., Awaitable[None]]] = {
            '/help': self.show_help,
            '/clear': self.clear_conversation,
            '/config': self.show_config,
            '/memory': self.edit_memory,
            '/status': self.show_status,
            '/init': self.initialize_project_guide,
            '/exit': self.exit_repl,
            '/quit': self.exit_repl,
            '/cwd': self.show_cwd,
            '/cd': self.change_directory,
            '/history': self.show_history,
            '/permissions': self.show_permissions,
            '/compact': self.compact_session,
        }

    async def execute(self, command_input: str):
        """Parse and execute a slash command."""
        parts = command_input.split(maxsplit=1)
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        if command_name in self.commands:
            try:
                await self.commands[command_name](args)
            except Exception as e:
                print(f"❌ Error executing {command_name}: {e}")
        else:
            print(f"❓ Unknown command: {command_name}. Try /help.")

    async def show_help(self, args: str):
        """Display help information for slash commands."""
        print("\n🤖 Claude Code-style Terminal Assistant Help:")
        print("-----------------------------------------")
        print("Available slash commands:")
        for cmd, func in self.commands.items():
            doc = func.__doc__.strip().split('\n')[0] if func.__doc__ else "No description."
            print(f"  {cmd:<15} - {doc}")
        print("\nNatural Language:")
        print("  Type your requests in plain English. Examples:")
        print("    'read the file main.py and tell me what it does'")
        print("    'find all TODO comments in the src directory'")
        print("    'what are the main dependencies of this project?'")
        print("\nMemory Shortcut:")
        print("  `# your memory text` - Quickly add text to memory (CLAUDE.md).")
        print("\nMultiline Input:")
        print("  End a line with `\\` to continue on the next line.")
        print("-----------------------------------------")

    async def clear_conversation(self, args: str):
        """Clear the current conversation history."""
        self.repl.conversation_history.clear()
        self.repl.session_manager.session_data['conversation'] = []
        print("🧹 Conversation history cleared.")

    async def show_config(self, args: str):
        """View or modify configuration (basic)."""
        print("\n⚙️ Configuration (Basic View):")
        print(f"  Working Directory: {Path.cwd()}")
        print(f"  User Memory Path: {self.repl.context_manager.user_memory_file}")
        print(f"  Project Memory Path: {self.repl.context_manager.project_memory_file}")
        if self.repl.use_mcp:
            print(f"  MCP Enabled: Yes (URL: {self.repl.mcp_server_url})")
        else:
            print("  MCP Enabled: No")

    async def edit_memory(self, args: str):
        """Edit CLAUDE.md memory files."""
        print("\n💾 Edit Memory Files:")
        print("  1. Project Memory (./CLAUDE.md)")
        print("  2. User Memory (~/.claude/CLAUDE.md)")
        choice = input("  Select file to edit (1-2, or path): ").strip()

        file_to_edit = None
        if choice == '1':
            file_to_edit = self.repl.context_manager.project_memory_file
            self.repl.context_manager._ensure_project_memory_exists()
        elif choice == '2':
            file_to_edit = self.repl.context_manager.user_memory_file
            self.repl.context_manager._ensure_user_memory_exists()
        elif choice:
            file_to_edit = Path(choice).resolve()

        if file_to_edit:
            editor = os.environ.get('EDITOR', 'nano')
            try:
                print(f"  Opening {file_to_edit} with {editor}...")
                subprocess.run([editor, str(file_to_edit)], check=True)
                print(f"  Finished editing {file_to_edit}.")
                # Reload memories after editing
                self.repl.context_manager.load_project_memory()
                self.repl.context_manager.load_user_memory()
                print("  Memory reloaded.")
            except FileNotFoundError:
                print(f"  ❌ Editor '{editor}' not found. Please set your EDITOR environment variable.")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Error opening/editing file: {e}")
            except Exception as e:
                print(f"  ❌ An unexpected error occurred: {e}")
        else:
            print("  No file selected or invalid choice.")

    async def show_status(self, args: str):
        """View account and system statuses (basic)."""
        print("\n📊 System Status:")
        print(f"  Current Session ID: {self.repl.current_session_id}")
        print(f"  Conversation Length: {len(self.repl.conversation_history)} messages")
        print(f"  Python Version: {sys.version.split()[0]}")
        print(f"  CodexSimulator Version: 0.1.0")

    async def initialize_project_guide(self, args: str):
        """Initialize project with a CLAUDE.md guide."""
        project_claude_md = Path.cwd() / "CLAUDE.md"
        if project_claude_md.exists():
            overwrite = input(f"'{project_claude_md}' already exists. Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Skipped CLAUDE.md initialization.")
                return

        initial_content = f"""# Claude Project Guide: {Path.cwd().name}

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project Root: {Path.cwd()}

## Overview
<!-- Describe the project's purpose, main technologies, and key components. -->
Example: This project is a Python-based web server using Flask and SQLAlchemy.

## Getting Started
<!-- Provide brief instructions on how to set up and run the project. -->
Example:
1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `flask run`

## Key Modules/Directories
<!-- List important parts of the codebase. -->
- `src/`: Main application code
- `tests/`: Unit and integration tests
- `docs/`: Project documentation

## Coding Standards
<!-- Outline any project-specific coding conventions. -->
- Follow PEP 8 guidelines.
- Use type hints for all function signatures.
- Write docstrings for all public modules, classes, and functions.

## Common Commands & Workflows
<!-- List frequently used commands or operational procedures. -->
- `pytest`: Run all tests.
- `pylint src/`: Lint the codebase.
- `git commit -m "feat: <description>"`: Commit message format.

## Important Notes
<!-- Any other critical information for someone working on this project. -->

---
*This file is automatically loaded as context for Claude interactions.*
*You can edit this file directly or use the `/memory` command.*
"""
        try:
            project_claude_md.write_text(initial_content, encoding='utf-8')
            print(f"✅ Initialized project guide at {project_claude_md}")
            self.repl.context_manager.load_project_memory()
        except Exception as e:
            print(f"❌ Failed to initialize CLAUDE.md: {e}")

    async def exit_repl(self, args: str):
        """Exit the REPL session."""
        print("👋 Exiting Claude Code-style Terminal Assistant...")
        self.repl.stop()

    async def show_cwd(self, args: str):
        """Show the current working directory."""
        print(f"📁 Current working directory: {Path.cwd()}")

    async def change_directory(self, args: str):
        """Change the current working directory."""
        if not args:
            print("Usage: /cd <directory_path>")
            return
        
        new_dir = Path(args).expanduser()
        try:
            os.chdir(new_dir)
            print(f"📁 Changed working directory to: {Path.cwd()}")
            # Reload project-specific CLAUDE.md if it exists
            self.repl.context_manager.load_project_memory(reload=True)
        except FileNotFoundError:
            print(f"❌ Directory not found: {new_dir}")
        except Exception as e:
            print(f"❌ Failed to change directory: {e}")

    async def show_history(self, args: str):
        """Show conversation history."""
        print("\n📜 Conversation History:")
        if not self.repl.conversation_history:
            print("  No history yet.")
            return
        
        for i, entry in enumerate(self.repl.conversation_history):
            role = entry.get("role", "unknown").capitalize()
            content = entry.get("content", "")
            print(f"  [{i+1}] {role}: {content[:80]}{'...' if len(content) > 80 else ''}")

    async def show_permissions(self, args: str):
        """Show current permission settings."""
        print("\n🔐 Current Permissions:")
        permissions = self.repl.permission_manager.list_permissions()
        
        print("  Session Allowed:")
        if permissions['session']:
            for p_rule in permissions['session']: 
                print(f"    - {p_rule}")
        else:
            print("    (None)")
            
        print("\n  Permanently Allowed (from settings.json):")
        if permissions['permanent']:
            for p_rule in permissions['permanent']: 
                print(f"    - {p_rule}")
        else:
            print("    (None)")

        print("\n  Denied (from settings.json):")
        if permissions['denied']:
            for p_rule in permissions['denied']: 
                print(f"    - {p_rule}")
        else:
            print("    (None)")
        
        print("\nNote: Read-only tools are always allowed without explicit listing.")
        print("Use `/config` or edit settings.json files to manage permanent permissions.")

    async def compact_session(self, args: str):
        """Compact the current session's conversation history."""
        instructions = args.strip()
        print(f"📝 Compacting session (instructions: '{instructions if instructions else 'None'}')...")
        self.repl.session_manager.compact_session(
            session_id=self.repl.current_session_id,
            instructions=instructions
        )
        print("Session data for saving has been compacted. Current REPL history remains.")

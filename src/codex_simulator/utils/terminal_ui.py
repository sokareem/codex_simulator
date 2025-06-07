"""Enhanced terminal UI utilities using Rich for better user experience with Nature's Way Philosophy integration."""

import sys
import time
from typing import Any, Dict, Optional

# Try to import rich and prompt_toolkit with graceful fallbacks
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    from rich import print as rich_print
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

# Import nature-inspired UI components
try:
    from .nature_ui import nature_ui
    from .nature_welcome import create_nature_welcome
    from .nature_integration import nature_integration
    NATURE_UI_AVAILABLE = True
except ImportError:
    NATURE_UI_AVAILABLE = False

class TerminalUI:
    """Enhanced terminal UI with Rich formatting and interactive prompts."""
    
    def __init__(self):
        self.rich_available = RICH_AVAILABLE
        self.prompt_toolkit_available = PROMPT_TOOLKIT_AVAILABLE
        
        if self.rich_available:
            self.console = Console()
        
        if self.prompt_toolkit_available:
            self.history = InMemoryHistory()
            self.command_completer = WordCompleter([
                'help', 'exit', 'quit', 'clear', 'ls', 'cd', 'pwd', 'cat', 'grep',
                'find', 'ps', 'top', 'df', 'du', 'free', 'uname', 'whoami'
            ])
        
    def print_ai_response(self, message: str, title: str = "AI Assistant"):
        """Print AI response with styled formatting - Enhanced with Nature's Way principles."""
        # Use nature UI if available, fall back to enhanced traditional
        if NATURE_UI_AVAILABLE:
            nature_ui.print_ase_response(message, title, include_wisdom=True)
        elif self.rich_available:
            # Enhanced traditional with more natural colors
            panel = Panel(
                message,
                title=f"[bold green]🌿 {title} 🌿[/bold green]",
                border_style="bright_green",
                padding=(1, 2),
                subtitle="[dim cyan]Àjọ pọ̀ là ń gun òrò - Together we climb the mountain[/dim cyan]"
            )
            self.console.print(panel)
        else:
            # Fallback to simple print with nature elements
            print(f"\n🌿 === {title} === 🌿")
            print(message)
            print("🌿" + "=" * (len(title) + 8) + "🌿")
        
    def print_system_message(self, message: str, level: str = "info"):
        """Print system messages with appropriate styling - Enhanced with nature elements."""
        if NATURE_UI_AVAILABLE:
            # Map traditional levels to nature concepts
            nature_level_map = {
                "info": "flow",
                "warning": "warning", 
                "error": "earth",
                "success": "success"
            }
            nature_ui.print_nature_message(message, nature_level_map.get(level, "flow"))
        elif self.rich_available:
            # Enhanced nature-inspired colors
            colors = {
                "info": "bright_cyan",
                "warning": "bright_yellow", 
                "error": "bright_red",
                "success": "bright_green"
            }
            symbols = {
                "info": "🌊",
                "warning": "⚡", 
                "error": "🌋",
                "success": "🌺"
            }
            color = colors.get(level, "white")
            symbol = symbols.get(level, "🌿")
            self.console.print(f"[{color}]{symbol} {message}[/{color}]")
        else:
            # Fallback to simple print with nature emoji
            emoji_map = {
                "info": "🌊",
                "warning": "⚡", 
                "error": "🌋",
                "success": "🌺"
            }
            emoji = emoji_map.get(level, "🌿")
            print(f"{emoji} {message}")
        
    def print_command_output(self, output: str, command: str = ""):
        """Print command output with syntax highlighting."""
        if command:
            if self.rich_available:
                self.console.print(f"[dim]$ {command}[/dim]")
            else:
                print(f"$ {command}")
        
        if output.strip():
            if self.rich_available:
                # Try to detect and highlight code/structured output
                try:
                    if output.startswith('{') or output.startswith('['):
                        syntax = Syntax(output, "json", theme="monokai", line_numbers=False)
                        self.console.print(syntax)
                    else:
                        self.console.print(output)
                except:
                    self.console.print(output)
            else:
                print(output)
                
    def show_progress(self, description: str = "Processing..."):
        """Create a progress spinner for long-running operations."""
        if self.rich_available:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            )
        else:
            # Simple fallback progress indicator
            class SimpleProgress:
                def __enter__(self):
                    print(f"⏳ {description}")
                    return self
                    
                def __exit__(self, *args):
                    print("✅ Done")
                    
                def add_task(self, description, total=None):
                    return 0
                    
                def update(self, task_id, completed=None):
                    pass
                    
            return SimpleProgress()
        
    def get_user_input(self, prompt_text: str = "❯ ") -> str:
        """Get user input with history and auto-completion - Enhanced with natural prompts."""
        # Use nature UI if available for adaptive prompts
        if NATURE_UI_AVAILABLE:
            try:
                from .nature_integration import get_nature_prompt
                nature_prompt = get_nature_prompt()
                if self.prompt_toolkit_available:
                    return prompt(
                        nature_prompt,
                        history=self.history,
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=self.command_completer
                    )
                else:
                    return input(nature_prompt)
            except ImportError:
                pass
        
        if self.prompt_toolkit_available:
            try:
                return prompt(
                    prompt_text,
                    history=self.history,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.command_completer
                )
            except (KeyboardInterrupt, EOFError):
                return ""
        else:
            # Fallback to basic input with nature prompt
            try:
                return input("🌿 " if not NATURE_UI_AVAILABLE else prompt_text)
            except (KeyboardInterrupt, EOFError):
                return ""
            
    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for potentially destructive actions."""
        if self.rich_available:
            return Confirm.ask(f"[yellow]{message}[/yellow]")
        else:
            response = input(f"{message} (y/N): ").lower()
            return response in ['y', 'yes']
        
    def display_table(self, data: list, headers: list, title: str = ""):
        """Display data in a formatted table."""
        if self.rich_available:
            table = Table(title=title, show_header=True)
            
            for header in headers:
                table.add_column(header, style="cyan")
                
            for row in data:
                table.add_row(*[str(cell) for cell in row])
                
            self.console.print(table)
        else:
            # Simple text table fallback
            if title:
                print(f"\n{title}")
                print("-" * len(title))
            
            # Print headers
            header_line = " | ".join(str(h).ljust(15) for h in headers)
            print(header_line)
            print("-" * len(header_line))
            
            # Print data rows
            for row in data:
                row_line = " | ".join(str(cell).ljust(15) for cell in row)
                print(row_line)
        
    def clear_screen(self):
        """Clear the terminal screen."""
        if self.rich_available:
            self.console.clear()
        else:
            # Fallback screen clear
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_welcome(self):
        """Print welcome message with branding - Enhanced with Nature's Way Philosophy."""
        if NATURE_UI_AVAILABLE:
            # Use fully natural welcome experience
            try:
                nature_ui.print_welcome_ase()
                return
            except Exception as e:
                print(f"⚠️  Nature welcome failed, using fallback: {e}")
        
        # Enhanced traditional welcome with nature elements
        try:
            if NATURE_UI_AVAILABLE:
                welcome_text = create_nature_welcome("Sinmi", "terminal")
            else:
                welcome_text = """🌳 CodeX Simulator Terminal Assistant
🌿 Intelligent AI-powered terminal interaction

Type 'help' for available commands or start asking questions!
Àṣẹ - May your commands manifest with power! 🌟"""
        except Exception:
            welcome_text = """🌳 CodeX Simulator Terminal Assistant
🌿 Intelligent AI-powered terminal interaction

Type 'help' for available commands or start asking questions!
Àṣẹ - May your commands manifest with power! 🌟"""
        
        if self.rich_available:
            formatted_text = f"""
[bold bright_green]🌳 CodeX Simulator Terminal Assistant[/bold bright_green]
[dim bright_cyan]🌿 Where technology meets ancient wisdom[/dim bright_cyan]

[bright_yellow]Kú àárọ̀, Sinmi! Welcome to your digital forest.[/bright_yellow]

{welcome_text}

[dim]Type 'help' for commands, 'wisdom' for inspiration, or ask anything![/dim]
[dim]Àṣẹ - May your commands manifest with power! 🌟[/dim]
            """
            self.console.print(Panel(formatted_text, border_style="bright_green"))
        else:
            print("\n" + "🌿" * 60)
            print(welcome_text)
            print("🌿" * 60)

# Global instance
terminal_ui = TerminalUI()

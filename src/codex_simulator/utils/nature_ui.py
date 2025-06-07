"""
Nature's Way UI - Enhanced terminal interface inspired by natural patterns and Yoruba philosophy
"""

import sys
import time
import random
from typing import Any, Dict, Optional, List
from datetime import datetime

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
    from rich.align import Align
    from rich.columns import Columns
    from rich.tree import Tree
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


class NatureUI:
    """
    Nature-inspired terminal UI that embodies organic flow, Yoruba wisdom, and natural harmony.
    
    Philosophy:
    - Àṣẹ (life force) flows through all interactions
    - Ifá wisdom guides adaptive responses
    - Ubuntu philosophy: "I am because we are"
    - Seasonal and time-of-day awareness
    - Organic color palettes inspired by earth, water, fire, air
    """
    
    def __init__(self):
        self.rich_available = RICH_AVAILABLE
        self.prompt_toolkit_available = PROMPT_TOOLKIT_AVAILABLE
        
        if self.rich_available:
            self.console = Console()
        
        if self.prompt_toolkit_available:
            self.history = InMemoryHistory()
            # Enhanced command completion with natural language
            self.command_completer = WordCompleter([
                'help', 'àjé' , 'exit', 'òwó', 'clear', 'omi', 'ls', 'cd', 'pwd', 
                'cat', 'grep', 'find', 'explore', 'discover', 'flow', 'harmony',
                'balance', 'wisdom', 'àṣẹ', 'yoruba', 'proverb'
            ])
        
        # Natural color themes based on time of day and seasons
        self.current_palette = self._get_natural_palette()
        
        # Yoruba proverbs for wisdom integration
        self.yoruba_wisdom = [
            ("Àgbẹbọ̀ ló ń gun àgbẹbọ̀", "It takes a skilled farmer to climb a palm tree - Mastery comes from dedication"),
            ("Ẹni tó bá ní sùúrù á jeun ẹyọ àgbon", "One who has patience will eat the pulp of coconut - Good things come to those who wait"),
            ("Bí a bá ní láti tún ayé ṣe", "If we were to remake the world - Speaking of perfection or ideal situations"),
            ("Àjàgbára kì í jà nítorí òun nìkan", "The strong don't fight for themselves alone - Leadership is service"),
            ("Ọwọ́ kan ò gb'òkú ní agbon", "One hand cannot lift the coconut - Unity is strength")
        ]
        
    def _get_natural_palette(self) -> Dict[str, str]:
        """Get color palette based on time of day and season."""
        hour = datetime.now().hour
        month = datetime.now().month
        
        # Time-of-day palettes
        if 5 <= hour < 8:  # Dawn
            return {
                "primary": "rgb(255,183,77)",  # Golden sunrise
                "secondary": "rgb(255,138,101)",  # Warm orange
                "accent": "rgb(162,210,255)",  # Morning sky
                "text": "rgb(139,69,19)",  # Earth brown
                "wisdom": "rgb(218,165,32)"  # Goldenrod
            }
        elif 8 <= hour < 17:  # Day
            return {
                "primary": "rgb(34,139,34)",  # Forest green
                "secondary": "rgb(60,179,113)",  # Medium sea green
                "accent": "rgb(135,206,235)",  # Sky blue
                "text": "rgb(85,107,47)",  # Dark olive green
                "wisdom": "rgb(184,134,11)"  # Dark goldenrod
            }
        elif 17 <= hour < 20:  # Sunset
            return {
                "primary": "rgb(205,92,92)",  # Indian red
                "secondary": "rgb(255,140,0)",  # Dark orange
                "accent": "rgb(138,43,226)",  # Blue violet
                "text": "rgb(139,69,19)",  # Saddle brown
                "wisdom": "rgb(189,183,107)"  # Dark khaki
            }
        else:  # Night
            return {
                "primary": "rgb(75,0,130)",  # Indigo
                "secondary": "rgb(72,61,139)",  # Dark slate blue
                "accent": "rgb(176,196,222)",  # Light steel blue
                "text": "rgb(169,169,169)",  # Dark gray
                "wisdom": "rgb(147,112,219)"  # Medium purple
            }
    
    def print_ase_response(self, message: str, title: str = "Àṣẹ Assistant", include_wisdom: bool = False):
        """Print AI response with natural, flowing design and optional Yoruba wisdom."""
        if self.rich_available:
            # Create organic border using natural characters
            border_chars = "🌿🌱🍃🌾"
            border = "".join(random.choices(border_chars, k=3))
            
            # Add wisdom if requested
            if include_wisdom and random.random() < 0.3:  # 30% chance
                proverb_yoruba, proverb_english = random.choice(self.yoruba_wisdom)
                wisdom_text = f"\n[dim italic]{proverb_yoruba}[/dim italic]\n[dim]{proverb_english}[/dim]\n"
                message = wisdom_text + message
            
            panel = Panel(
                message,
                title=f"[bold {self.current_palette['primary']}]{border} {title} {border}[/bold {self.current_palette['primary']}]",
                border_style=self.current_palette['secondary'],
                padding=(1, 2),
                subtitle=f"[dim {self.current_palette['accent']}]Àjọ pọ̀ là ń gun òrò - Together we climb the mountain[/dim {self.current_palette['accent']}]"
            )
            self.console.print(panel)
        else:
            # Beautiful fallback
            print("\n" + "🌿" * 50)
            print(f"   {title}")
            if include_wisdom and random.random() < 0.3:
                proverb_yoruba, proverb_english = random.choice(self.yoruba_wisdom)
                print(f"\n   💫 {proverb_yoruba}")
                print(f"   💫 {proverb_english}\n")
            print(message)
            print("🌿" * 50)
    
    def print_nature_message(self, message: str, level: str = "flow"):
        """Print system messages with nature-inspired styling."""
        nature_symbols = {
            "flow": "🌊",
            "growth": "🌱", 
            "wisdom": "🦉",
            "warning": "⚡",
            "harmony": "🕊️",
            "success": "🌺",
            "earth": "🌍"
        }
        
        if self.rich_available:
            symbol = nature_symbols.get(level, "🌿")
            color = self.current_palette.get(level, self.current_palette['text'])
            self.console.print(f"[{color}]{symbol} {message}[/{color}]")
        else:
            symbol = nature_symbols.get(level, "🌿")
            print(f"{symbol} {message}")
    
    def show_organic_progress(self, description: str = "Flowing like water..."):
        """Create a progress indicator that feels organic and natural."""
        if self.rich_available:
            # Custom spinner with nature symbols
            nature_spinners = ["🌱", "🌿", "🍃", "🌾", "🌸", "🌺", "🦋", "🌊"]
            
            class OrganicProgress:
                def __init__(self):
                    self.console = Console()
                    
                def __enter__(self):
                    print(f"🌊 {description}")
                    return self
                    
                def __exit__(self, *args):
                    print("🌺 Flow complete")
                    
                def add_task(self, description, total=None):
                    return 0
                    
                def update(self, task_id, completed=None):
                    pass
                    
            return OrganicProgress()
        else:
            class SimpleOrganicProgress:
                def __enter__(self):
                    print(f"🌊 {description}")
                    return self
                    
                def __exit__(self, *args):
                    print("🌺 Complete")
                    
                def add_task(self, description, total=None):
                    return 0
                    
                def update(self, task_id, completed=None):
                    pass
                    
            return SimpleOrganicProgress()
    
    def get_natural_input(self, prompt_text: str = "🌿 ") -> str:
        """Get user input with natural, flowing prompt."""
        # Adaptive prompt based on time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            prompt_text = "🌅 "  # Dawn/morning
        elif 12 <= hour < 17:
            prompt_text = "☀️ "   # Midday
        elif 17 <= hour < 20:
            prompt_text = "🌅 "  # Sunset
        else:
            prompt_text = "🌙 "   # Night
            
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
            try:
                return input(prompt_text)
            except (KeyboardInterrupt, EOFError):
                return ""
    
    def confirm_with_wisdom(self, message: str) -> bool:
        """Get user confirmation with Yoruba wisdom."""
        if self.rich_available:
            wisdom_message = f"[{self.current_palette['wisdom']}]{message}[/{self.current_palette['wisdom']}]\n[dim]Ìbéèrè ni ìbẹ̀rẹ̀ ọgbọ́n - Questions are the beginning of wisdom[/dim]"
            return Confirm.ask(wisdom_message)
        else:
            print(f"{message}")
            print("Ìbéèrè ni ìbẹ̀rẹ̀ ọgbọ́n - Questions are the beginning of wisdom")
            response = input("(y/N): ").lower()
            return response in ['y', 'yes', 'bẹ́ẹ̀ni']
    
    def display_organic_table(self, data: list, headers: list, title: str = ""):
        """Display data in a nature-inspired table format."""
        if self.rich_available:
            table = Table(
                title=f"🌳 {title}" if title else "",
                show_header=True,
                border_style=self.current_palette['secondary'],
                title_style=f"bold {self.current_palette['primary']}"
            )
            
            for i, header in enumerate(headers):
                # Alternate column styles for organic feel
                style = self.current_palette['accent'] if i % 2 == 0 else self.current_palette['text']
                table.add_column(header, style=style)
                
            for row in data:
                table.add_row(*[str(cell) for cell in row])
                
            self.console.print(table)
        else:
            # Organic text table with natural borders
            if title:
                print(f"\n🌳 {title}")
                print("🌿" + "─" * (len(title) + 2) + "🌿")
            
            # Headers with nature styling
            header_line = " 🌱 ".join(str(h).ljust(15) for h in headers)
            print(f"🌱 {header_line} 🌱")
            print("🌿" + "─" * len(header_line) + "🌿")
            
            # Data rows
            for row in data:
                row_line = " 🍃 ".join(str(cell).ljust(15) for cell in row)
                print(f"🍃 {row_line} 🍃")
    
    def print_welcome_ase(self):
        """Print nature-inspired welcome message with Yoruba greetings."""
        welcome_yoruba = "Kú àárọ̀! Àṣẹ - May your commands flow with power!"
        welcome_english = "CodeX Simulator - Nature's Way Terminal Assistant"
        subtitle = "Where technology meets ancient wisdom"
        
        if self.rich_available:
            # Create tree-like structure for welcome
            welcome_tree = Tree(
                f"[bold {self.current_palette['primary']}]🌳 {welcome_english}[/bold {self.current_palette['primary']}]"
            )
            welcome_tree.add(f"[{self.current_palette['secondary']}]🌿 {welcome_yoruba}[/{self.current_palette['secondary']}]")
            welcome_tree.add(f"[dim {self.current_palette['accent']}]✨ {subtitle}[/dim {self.current_palette['accent']}]")
            
            # Add seasonal greeting
            season = self._get_season_greeting()
            welcome_tree.add(f"[{self.current_palette['wisdom']}]{season}[/{self.current_palette['wisdom']}]")
            
            panel = Panel(
                Align.center(welcome_tree),
                border_style=self.current_palette['secondary'],
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print("\n" + "🌿" * 60)
            print(f"    🌳 {welcome_english}")
            print(f"    🌿 {welcome_yoruba}")
            print(f"    ✨ {subtitle}")
            print(f"    {self._get_season_greeting()}")
            print("🌿" * 60)
    
    def _get_season_greeting(self) -> str:
        """Get seasonal greeting based on current time."""
        month = datetime.now().month
        
        if month in [12, 1, 2]:  # Winter
            return "❄️ Àkókò òtútù - Time of reflection and inner growth"
        elif month in [3, 4, 5]:  # Spring  
            return "🌸 Àkókò ìgbòsàn - Time of new beginnings and fresh growth"
        elif month in [6, 7, 8]:  # Summer
            return "☀️ Àkókò ọ̀rọ̀ - Time of abundance and full energy"
        else:  # Fall
            return "🍂 Àkókò ìkórè - Time of harvest and gratitude"
    
    def clear_with_intention(self):
        """Clear screen with mindful intention."""
        if self.rich_available:
            self.console.clear()
            # Brief pause for mindfulness
            self.console.print("[dim]🧘 Clearing space for new possibilities...[/dim]")
            time.sleep(0.5)
        else:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
            print("🧘 Space cleared with intention...")
    
    def breathe_pause(self, duration: float = 1.0):
        """Natural pause that encourages mindful breathing."""
        if self.rich_available:
            for i in range(3):
                self.console.print("[dim]🫁 Inhale...[/dim]", end="")
                time.sleep(duration/6)
                self.console.print("[dim] Exhale...[/dim]")
                time.sleep(duration/6)
        else:
            time.sleep(duration)

# Global instance
nature_ui = NatureUI()

"""
Organic Progress Indicators for Nature's Way UI
Progress that breathes, flows, and feels alive
"""

import time
import random
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class OrganicProgressIndicator:
    """
    Progress indicators that feel organic and alive, inspired by natural processes.
    
    Features:
    - Breathing rhythm progress bars
    - Nature-inspired spinners
    - Seasonal adaptation
    - Mindful pacing with natural pauses
    - Wisdom integration during long processes
    """
    
    def __init__(self):
        self.rich_available = RICH_AVAILABLE
        if self.rich_available:
            self.console = Console()
        
        # Nature-inspired spinners for different seasons
        self.seasonal_spinners = {
            "spring": ["🌱", "🌿", "🍃", "🌸", "🌺", "🦋"],
            "summer": ["☀️", "🌻", "🔥", "🍯", "⚡", "✨"],
            "autumn": ["🍂", "🍁", "🌰", "🎃", "🦔", "🍄"],
            "winter": ["❄️", "🌨️", "⭐", "🕯️", "🦉", "🌙"]
        }
        
        # Growth process metaphors
        self.growth_stages = [
            ("🌱", "Planting seeds of intention..."),
            ("🌿", "First shoots of possibility emerging..."),
            ("🍃", "Ideas unfurling like young leaves..."),
            ("🌸", "Blossoming into understanding..."),
            ("🌺", "Full bloom of insight achieved..."),
            ("🍯", "Sweet essence of wisdom distilled...")
        ]
        
        # Breathing rhythms (in seconds)
        self.breathing_patterns = {
            "calm": {"inhale": 4, "hold": 2, "exhale": 6},
            "energetic": {"inhale": 3, "hold": 1, "exhale": 4},
            "deep": {"inhale": 6, "hold": 4, "exhale": 8},
            "quick": {"inhale": 2, "hold": 1, "exhale": 3}
        }
        
        # Wisdom for long processes
        self.patience_wisdom = [
            ("Yoruba", "Sùúrù ni bàbá ìwà", "Patience is the father of character"),
            ("Nature", "🌳", "Great oaks grow slowly but stand for centuries"),
            ("Ubuntu", "🤝", "The river that moves slowly still reaches the ocean"),
            ("Seasonal", "🌱", "Every season has its purpose in the greater cycle")
        ]
    
    def _get_current_season(self) -> str:
        """Determine current season for appropriate spinner selection."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def breathing_progress(self, duration: float = 10.0, message: str = "Centering thoughts..."):
        """
        A progress indicator that follows breathing rhythm.
        """
        if not self.rich_available:
            print(f"🫁 {message}")
            time.sleep(duration)
            print("✨ Centered and ready")
            return
        
        pattern = self.breathing_patterns["calm"]
        total_cycle = pattern["inhale"] + pattern["hold"] + pattern["exhale"]
        cycles = int(duration / total_cycle)
        
        with Live(self.console) as live:
            for cycle in range(cycles):
                # Inhale
                for i in range(pattern["inhale"]):
                    progress = (i + 1) / pattern["inhale"]
                    bar = "🫁 " + "○" * int(progress * 10) + "●" * (10 - int(progress * 10))
                    text = Text(f"{message}\n{bar}\nInhale... ({cycle + 1}/{cycles})")
                    live.update(Align.center(text))
                    time.sleep(1)
                
                # Hold
                for i in range(pattern["hold"]):
                    bar = "💫 " + "●" * 10
                    text = Text(f"{message}\n{bar}\nHold... ({cycle + 1}/{cycles})")
                    live.update(Align.center(text))
                    time.sleep(1)
                
                # Exhale
                for i in range(pattern["exhale"]):
                    progress = (pattern["exhale"] - i) / pattern["exhale"]
                    bar = "🌬️ " + "●" * int(progress * 10) + "○" * (10 - int(progress * 10))
                    text = Text(f"{message}\n{bar}\nExhale... ({cycle + 1}/{cycles})")
                    live.update(Align.center(text))
                    time.sleep(1)
        
        self.console.print("✨ [green]Centered and ready[/green]")
    
    def growth_progress(self, stages: List[str], stage_duration: float = 2.0):
        """
        Progress through stages like natural growth.
        """
        if not self.rich_available:
            for i, stage in enumerate(stages):
                print(f"{self.growth_stages[i % len(self.growth_stages)][0]} {stage}")
                time.sleep(stage_duration)
            return
        
        with Live(self.console) as live:
            for i, stage in enumerate(stages):
                symbol, metaphor = self.growth_stages[i % len(self.growth_stages)]
                
                # Animate the growth process
                for frame in range(int(stage_duration * 4)):  # 4 FPS
                    dots = "." * ((frame % 3) + 1)
                    text = Text(f"{symbol} {stage}{dots}\n[dim italic]{metaphor}[/dim italic]")
                    live.update(Align.center(text))
                    time.sleep(0.25)
        
        self.console.print("🌺 [bold green]Growth cycle complete![/bold green]")
    
    def seasonal_spinner(self, duration: float = 5.0, message: str = "Processing naturally..."):
        """
        Spinner that uses seasonal symbols and adapts to time of year.
        """
        season = self._get_current_season()
        spinner_chars = self.seasonal_spinners[season]
        
        if not self.rich_available:
            print(f"🌿 {message}")
            for i in range(int(duration)):
                print(f"\r{spinner_chars[i % len(spinner_chars)]} Working...", end="", flush=True)
                time.sleep(1)
            print(f"\n✨ Complete!")
            return
        
        with Live(self.console) as live:
            start_time = time.time()
            frame = 0
            
            while time.time() - start_time < duration:
                char = spinner_chars[frame % len(spinner_chars)]
                elapsed = time.time() - start_time
                
                # Add breathing pause every few seconds
                if int(elapsed) % 4 == 0 and elapsed > 0:
                    char = "🫁"  # Breathing pause
                
                text = Text(f"{char} {message}\n[dim]Flowing with the rhythm of {season}...[/dim]")
                live.update(Align.center(text))
                
                time.sleep(0.3)
                frame += 1
        
        self.console.print("🌺 [bold green]Natural process complete![/bold green]")
    
    def wisdom_progress(self, duration: float = 15.0, show_wisdom_interval: float = 5.0):
        """
        Long process with periodic wisdom sharing to maintain engagement.
        """
        wisdom_shown = 0
        start_time = time.time()
        
        if not self.rich_available:
            print("🌊 Deep process beginning...")
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                if elapsed > (wisdom_shown + 1) * show_wisdom_interval:
                    culture, yoruba, english = random.choice(self.patience_wisdom)
                    print(f"\n💫 {culture} Wisdom: {yoruba}")
                    print(f"   {english}\n")
                    wisdom_shown += 1
                time.sleep(1)
            print("✨ Deep process complete")
            return
        
        with Live(self.console) as live:
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                progress = elapsed / duration
                
                # Show wisdom at intervals
                if elapsed > (wisdom_shown + 1) * show_wisdom_interval:
                    culture, yoruba, english = random.choice(self.patience_wisdom)
                    wisdom_text = f"💫 {culture} Wisdom: {yoruba}\n[dim]{english}[/dim]"
                    wisdom_shown += 1
                else:
                    # Regular progress display
                    bar_length = 20
                    filled = int(progress * bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    wisdom_text = f"🌊 Deep processing in progress...\n{bar} {progress:.1%}"
                
                text = Text(wisdom_text)
                live.update(Align.center(text))
                time.sleep(0.5)
        
        self.console.print("🌺 [bold green]Deep wisdom process complete![/bold green]")
    
    def create_custom_organic_progress(self, 
                                     total_steps: int,
                                     step_names: List[str],
                                     breathing_pauses: bool = True,
                                     wisdom_integration: bool = True) -> 'OrganicProgressContext':
        """
        Create a custom organic progress context manager.
        """
        return OrganicProgressContext(
            self, total_steps, step_names, breathing_pauses, wisdom_integration
        )


class OrganicProgressContext:
    """Context manager for organic progress tracking."""
    
    def __init__(self, 
                 indicator: OrganicProgressIndicator,
                 total_steps: int,
                 step_names: List[str],
                 breathing_pauses: bool,
                 wisdom_integration: bool):
        self.indicator = indicator
        self.total_steps = total_steps
        self.step_names = step_names
        self.breathing_pauses = breathing_pauses
        self.wisdom_integration = wisdom_integration
        self.current_step = 0
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        if self.indicator.rich_available:
            self.indicator.console.print("🌱 [bold green]Beginning organic process...[/bold green]")
        else:
            print("🌱 Beginning organic process...")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.indicator.rich_available:
            self.indicator.console.print("🌺 [bold green]Organic process complete![/bold green]")
        else:
            print("🌺 Organic process complete!")
    
    def update(self, message: str = ""):
        """Update progress to next step."""
        if self.current_step < len(self.step_names):
            step_name = self.step_names[self.current_step]
            symbol, metaphor = self.indicator.growth_stages[self.current_step % len(self.indicator.growth_stages)]
            
            if self.indicator.rich_available:
                self.indicator.console.print(f"{symbol} {step_name}")
                if message:
                    self.indicator.console.print(f"   [dim]{message}[/dim]")
            else:
                print(f"{symbol} {step_name}")
                if message:
                    print(f"   {message}")
            
            # Breathing pause between major steps
            if self.breathing_pauses and self.current_step > 0 and self.current_step % 3 == 0:
                if self.indicator.rich_available:
                    self.indicator.console.print("[dim]🫁 Natural pause for integration...[/dim]")
                time.sleep(1.5)
            
            self.current_step += 1
        
        # Wisdom at halfway point
        if (self.wisdom_integration and 
            self.current_step == self.total_steps // 2 and 
            len(self.indicator.patience_wisdom) > 0):
            culture, yoruba, english = random.choice(self.indicator.patience_wisdom)
            if self.indicator.rich_available:
                self.indicator.console.print(f"\n💫 [bold]{culture} Wisdom:[/bold] {yoruba}")
                self.indicator.console.print(f"   [dim italic]{english}[/dim italic]\n")
            else:
                print(f"\n💫 {culture} Wisdom: {yoruba}")
                print(f"   {english}\n")


# Global instance for easy access
organic_progress = OrganicProgressIndicator()

# Convenience functions
def show_breathing_progress(duration: float = 10.0, message: str = "Centering thoughts..."):
    """Show a breathing-rhythm progress indicator."""
    organic_progress.breathing_progress(duration, message)

def show_growth_progress(stages: List[str], stage_duration: float = 2.0):
    """Show progress through growth stages."""
    organic_progress.growth_progress(stages, stage_duration)

def show_seasonal_spinner(duration: float = 5.0, message: str = "Processing naturally..."):
    """Show a seasonal spinner."""
    organic_progress.seasonal_spinner(duration, message)

def show_wisdom_progress(duration: float = 15.0):
    """Show a long process with wisdom integration."""
    organic_progress.wisdom_progress(duration)

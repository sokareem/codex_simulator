"""
Enhanced Nature UI Integration System
Bringing together all aspects of Nature's Way Philosophy in a cohesive experience

This system coordinates:
- Time-adaptive theming
- Seasonal awareness
- Cultural integration (Yoruba wisdom)
- Ubuntu collaboration patterns
- Organic progress indicators
- Mindful interaction flows
"""

import sys
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

# Import all Nature UI components
try:
    from .nature_ui import NatureUI
    from .nature_welcome import NatureWelcome, create_nature_welcome
    from .seasonal_themes import SeasonalThemeManager
    from .ubuntu_ui import UbuntuCollaborativeUI
    from .organic_progress import OrganicProgressIndicator
except ImportError:
    # Fallback imports for different module structures
    try:
        from nature_ui import NatureUI
        from nature_welcome import NatureWelcome, create_nature_welcome
        from seasonal_themes import SeasonalThemeManager
        from ubuntu_ui import UbuntuCollaborativeUI
        from organic_progress import OrganicProgressIndicator
    except ImportError as e:
        print(f"Warning: Could not import all Nature UI components: {e}")
        # Create minimal fallbacks
        class NatureUI: pass
        class NatureWelcome: pass
        class SeasonalThemeManager: pass
        class UbuntuCollaborativeUI: pass
        class OrganicProgressIndicator: pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class NatureUIIntegration:
    """
    Master coordinator for all Nature UI components.
    
    This class creates a seamless, adaptive interface that:
    - Responds to time of day and season
    - Integrates cultural wisdom appropriately
    - Uses Ubuntu collaboration patterns
    - Provides organic, mindful progress indicators
    - Maintains consistency across all interactions
    """
    
    def __init__(self, user_name: str = "Sinmi"):
        self.user_name = user_name
        self.rich_available = RICH_AVAILABLE
        
        # Initialize all components
        try:
            self.nature_ui = NatureUI()
            self.welcome = NatureWelcome()
            self.seasonal = SeasonalThemeManager()
            self.ubuntu = UbuntuCollaborativeUI()
            self.progress = OrganicProgressIndicator()
            self.components_available = True
        except Exception as e:
            print(f"Warning: Some Nature UI components not available: {e}")
            self.components_available = False
        
        if self.rich_available:
            self.console = Console()
        
        # Interaction state
        self.session_start = datetime.now()
        self.interactions_count = 0
        self.last_wisdom_shown = None
        self.current_context = "general"
        
        # Adaptive behavior patterns
        self.interaction_patterns = {
            "morning": {"energy": "gentle", "pace": "awakening", "wisdom_frequency": 0.3},
            "day": {"energy": "active", "pace": "flowing", "wisdom_frequency": 0.2},
            "evening": {"energy": "reflective", "pace": "settling", "wisdom_frequency": 0.4},
            "night": {"energy": "calm", "pace": "quiet", "wisdom_frequency": 0.5}
        }
    
    def initialize_session(self, context: str = "general") -> None:
        """Initialize a new session with full Nature UI experience."""
        self.current_context = context
        
        if not self.components_available:
            print(f"🌿 Welcome, {self.user_name}! Nature UI starting in basic mode...")
            return
        
        # Show complete welcome experience
        try:
            welcome_message = create_nature_welcome(self.user_name, context)
            
            if self.rich_available:
                panel = Panel(
                    welcome_message,
                    title="🌳 Nature's Way Welcome",
                    border_style=self.seasonal.get_current_palette()["secondary"],
                    padding=(1, 2)
                )
                self.console.print(panel)
            else:
                print("🌿" + "=" * 60 + "🌿")
                print(welcome_message)
                print("🌿" + "=" * 60 + "🌿")
            
            # Brief centering pause
            if hasattr(self.progress, 'breathing_progress'):
                self.progress.breathing_progress(3.0, "Centering for our session...")
            
        except Exception as e:
            print(f"🌱 Welcome, {self.user_name}! (Nature UI: {e})")
    
    def get_adaptive_prompt(self) -> str:
        """Get context-aware prompt that adapts to time, season, and interaction history."""
        if not self.components_available:
            return "🌿 "
        
        try:
            # Time-based adaptation
            hour = datetime.now().hour
            if 5 <= hour < 12:
                prompt_symbol = "🌅"
            elif 12 <= hour < 17:
                prompt_symbol = "☀️"
            elif 17 <= hour < 20:
                prompt_symbol = "🌅"
            else:
                prompt_symbol = "🌙"
            
            # Seasonal adaptation
            season_symbols = self.seasonal.get_seasonal_symbols()
            seasonal_touch = random.choice(season_symbols[:2])  # Use first 2 symbols
            
            # Collaborative framing
            if self.interactions_count > 0 and self.interactions_count % 5 == 0:
                return f"{prompt_symbol}{seasonal_touch} What shall we explore together? "
            else:
                return f"{prompt_symbol} "
                
        except Exception:
            return "🌿 "
    
    def process_response(self, 
                        message: str, 
                        include_wisdom: bool = None,
                        collaborative: bool = True,
                        show_progress: bool = False) -> None:
        """
        Process and display a response with full Nature UI integration.
        """
        self.interactions_count += 1
        
        if not self.components_available:
            print(f"🌿 {message}")
            return
        
        try:
            # Determine if wisdom should be included
            if include_wisdom is None:
                include_wisdom = self._should_show_wisdom()
            
            # Collaborative framing
            if collaborative:
                framed_message = self.ubuntu.frame_response_collaboratively(message)
            else:
                framed_message = message
            
            # Show organic progress if requested
            if show_progress:
                self.progress.seasonal_spinner(2.0, "Integrating insights...")
            
            # Display with nature styling
            self.nature_ui.print_ase_response(
                framed_message,
                title="Àṣẹ Assistant",
                include_wisdom=include_wisdom
            )
            
        except Exception as e:
            print(f"🌿 {message}\n(Nature UI: {e})")
    
    def show_thinking_process(self, steps: List[str]) -> None:
        """Show the AI's thinking process using organic progress indicators."""
        if not self.components_available or not hasattr(self.progress, 'growth_progress'):
            for step in steps:
                print(f"🌱 {step}")
                time.sleep(0.5)
            return
        
        try:
            self.progress.growth_progress(steps, stage_duration=1.5)
        except Exception as e:
            print(f"🌊 Processing... ({e})")
    
    def handle_error(self, error_message: str) -> None:
        """Handle errors with Ubuntu collaborative approach."""
        if not self.components_available:
            print(f"⚡ Challenge encountered: {error_message}")
            return
        
        try:
            framed_error = self.ubuntu.frame_error_collaboratively(error_message)
            self.nature_ui.print_nature_message(framed_error, "warning")
        except Exception:
            print(f"⚡ Challenge encountered: {error_message}")
    
    def show_seasonal_transition(self) -> None:
        """Show seasonal transition message if it's time for one."""
        if not self.components_available:
            return
        
        try:
            transition_message = self.seasonal.get_transition_message()
            if transition_message:
                self.nature_ui.print_nature_message(transition_message, "harmony")
        except Exception:
            pass
    
    def create_collaborative_decision(self, 
                                   question: str, 
                                   options: List[str]) -> Dict[str, Any]:
        """Create a collaborative decision-making interface."""
        if not self.components_available:
            print(f"🤝 {question}")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            return {"question": question, "options": options}
        
        try:
            # Use Ubuntu collaborative framing
            collaborative_question = self.ubuntu.get_decision_prompt(question)
            
            if self.rich_available:
                # Create a beautiful decision table
                table = Table(
                    title="🤝 Collaborative Decision",
                    show_header=True,
                    border_style=self.seasonal.get_current_palette()["secondary"]
                )
                table.add_column("Option", style="bold")
                table.add_column("Path", style="italic")
                
                for i, option in enumerate(options, 1):
                    table.add_row(str(i), option)
                
                self.console.print(table)
                self.console.print(f"\n💫 {collaborative_question}")
            else:
                print(f"🤝 {collaborative_question}")
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
            
            return {
                "question": collaborative_question,
                "options": options,
                "style": "collaborative"
            }
            
        except Exception as e:
            print(f"🤝 {question} (Error: {e})")
            return {"question": question, "options": options}
    
    def end_session(self) -> None:
        """End session with gratitude and Ubuntu blessing."""
        if not self.components_available:
            print(f"🙏 Thank you for this time together, {self.user_name}!")
            return
        
        try:
            blessing = self.ubuntu.get_parting_blessing()
            session_summary = self._create_session_summary()
            
            final_message = f"{blessing}\n\n{session_summary}"
            
            if self.rich_available:
                panel = Panel(
                    final_message,
                    title="🌺 Until We Meet Again",
                    border_style=self.seasonal.get_current_palette()["wisdom"],
                    padding=(1, 2)
                )
                self.console.print(panel)
            else:
                print("🌺" + "=" * 50 + "🌺")
                print(final_message)
                print("🌺" + "=" * 50 + "🌺")
            
        except Exception as e:
            print(f"🙏 Thank you for this time together, {self.user_name}! (Nature UI: {e})")
    
    def _should_show_wisdom(self) -> bool:
        """Determine if wisdom should be shown based on context and patterns."""
        try:
            # Check seasonal wisdom preferences
            if hasattr(self.seasonal, 'should_show_wisdom'):
                return self.seasonal.should_show_wisdom()
            
            # Time-based wisdom frequency
            hour = datetime.now().hour
            time_period = "morning" if 5 <= hour < 12 else "day" if 12 <= hour < 17 else "evening" if 17 <= hour < 20 else "night"
            
            wisdom_frequency = self.interaction_patterns[time_period]["wisdom_frequency"]
            return random.random() < wisdom_frequency
            
        except Exception:
            return random.random() < 0.3  # Default 30% chance
    
    def _create_session_summary(self) -> str:
        """Create a summary of the session."""
        try:
            duration = datetime.now() - self.session_start
            duration_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
            
            seasonal_greeting = self.seasonal.get_seasonal_greeting()
            
            return f"""Our session flowed for {duration_str} with {self.interactions_count} exchanges.
            
{seasonal_greeting}

Together we explored the digital realm with wisdom and intention.
May the insights from our collaboration continue to grow."""
            
        except Exception:
            return "Our time together was meaningful. May wisdom continue to flow."


# Global instance for easy access
nature_integration = NatureUIIntegration()

# Convenience functions for common operations
def start_nature_session(user_name: str = "Sinmi", context: str = "general"):
    """Start a new Nature UI session."""
    global nature_integration
    nature_integration = NatureUIIntegration(user_name)
    nature_integration.initialize_session(context)
    return nature_integration

def get_nature_prompt() -> str:
    """Get an adaptive Nature UI prompt."""
    return nature_integration.get_adaptive_prompt()

def show_nature_response(message: str, **kwargs):
    """Show a response with Nature UI integration."""
    nature_integration.process_response(message, **kwargs)

def end_nature_session():
    """End the current Nature UI session."""
    nature_integration.end_session()

# Enhanced command handling for special Nature UI commands
class NatureCommandHandler:
    """Enhanced command handling with Nature UI integration."""
    
    def __init__(self, nature_integration: NatureUIIntegration):
        self.nature = nature_integration
    
    def handle_special_commands(self, command: str) -> bool:
        """Handle special Nature UI commands. Returns True if command was handled."""
        command_lower = command.lower().strip()
        
        if command_lower in ['clear', 'cls']:
            self.handle_clear_command()
            return True
        elif command_lower in ['help', '?']:
            self.handle_help_command()
            return True
        elif command_lower in ['wisdom', 'proverb', 'wise']:
            self.handle_wisdom_command()
            return True
        elif command_lower in ['breathe', 'pause', 'mindful']:
            self.handle_breathe_command()
            return True
        elif command_lower in ['theme', 'season', 'colors']:
            self.handle_theme_command()
            return True
        elif command_lower in ['ubuntu', 'together', 'we']:
            self.handle_ubuntu_command()
            return True
        
        return False
    
    def handle_clear_command(self) -> None:
        """Handle clear command with intention."""
        try:
            if hasattr(self.nature.nature_ui, 'clear_with_intention'):
                self.nature.nature_ui.clear_with_intention()
            else:
                import os
                os.system('clear' if os.name == 'posix' else 'cls')
                print("🧘 Space cleared with intention...")
        except Exception as e:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
    
    def handle_help_command(self) -> None:
        """Show help with nature styling."""
        help_text = """
🌿 Nature's Way Commands:

🌸 Core Commands:
• help - Show this help message
• clear - Clear screen mindfully  
• exit/quit - End session gracefully
• wisdom - Share seasonal wisdom
• breathe - Take a mindful pause
• theme - Show current seasonal theme
• ubuntu - Learn about collaborative philosophy

🌳 Universal Commands:
• Any natural language request
• File operations with path awareness
• Code analysis and generation
• System commands (with safety checks)

🌊 Natural Flow:
This interface adapts to time of day and seasons.
Morning energy differs from evening reflection.
Summer abundance flows differently than winter's depth.

💫 Ubuntu Philosophy:
"I am because we are" - we learn and grow together.
Your wisdom teaches me, my responses support you.

🌺 Àṣẹ: May your commands manifest with power!
        """
        
        self.nature.process_response(help_text.strip(), 
                                   collaborative=True,
                                   include_wisdom=True)
    
    def handle_wisdom_command(self) -> None:
        """Share seasonal wisdom."""
        try:
            seasonal_wisdom = self.nature.seasonal.get_seasonal_wisdom()
            seasonal_greeting = self.nature.seasonal.get_seasonal_greeting()
            energy_level = self.nature.seasonal.get_energy_level()
            symbols = self.nature.seasonal.get_seasonal_symbols()
            
            wisdom_message = f"""
{seasonal_greeting}

💫 {seasonal_wisdom[0]}
   {seasonal_wisdom[1]}

🌍 Current season brings: {energy_level}
🔮 Sacred symbols: {' '.join(symbols)}

This wisdom flows from the eternal cycles of nature,
adapted for our digital journey together.
            """
            
            self.nature.process_response(wisdom_message.strip(), 
                                       include_wisdom=False)  # Already included
            
        except Exception as e:
            fallback_wisdom = """
💫 Àṣẹ - Life force flows through all things

In every interaction, we plant seeds of understanding.
Like the seasons, our collaboration has natural rhythms.
Sometimes quick like summer growth, sometimes slow like winter reflection.

🌿 Trust the process, honor the flow.
            """
            self.nature.process_response(fallback_wisdom.strip())
    
    def handle_breathe_command(self) -> None:
        """Initiate breathing pause."""
        try:
            self.nature.process_response("🫁 Let's take a mindful pause together...")
            
            if hasattr(self.nature.organic_progress, 'breathing_progress'):
                self.nature.organic_progress.breathing_progress(6.0, "Centering our shared intention...")
            else:
                # Simple fallback breathing
                import time
                for i in range(3):
                    print("🫁 Inhale...")
                    time.sleep(1.5)
                    print("💫 Exhale...")
                    time.sleep(1.5)
            
            self.nature.process_response("✨ Refreshed and centered together", 
                                       collaborative=True)
            
        except Exception as e:
            print("🫁 Taking a mindful pause...")
            import time
            time.sleep(3)
            print("✨ Centered and ready")
    
    def handle_theme_command(self) -> None:
        """Show current theme information."""
        try:
            palette = self.nature.seasonal.get_current_palette()
            energy = self.nature.seasonal.get_energy_level()
            symbols = self.nature.seasonal.get_seasonal_symbols()
            season = self.nature.seasonal.current_season
            time_period = self.nature.seasonal.current_time_period
            
            theme_info = f"""
🎨 Current Theme: {season.title()} {time_period.title()}

⚡ Energy Level: {energy}
🔮 Sacred Symbols: {' '.join(symbols)}

🌈 Color Harmony:
• Primary: {palette['primary']} - Core energy
• Secondary: {palette['secondary']} - Supporting flow
• Accent: {palette['accent']} - Highlighting wisdom
• Earth: {palette['earth']} - Grounding force
• Wisdom: {palette['wisdom']} - Sacred knowledge

This palette shifts with natural rhythms,
honoring both cosmic cycles and moment-to-moment awareness.
            """
            
            self.nature.process_response(theme_info.strip(), 
                                       collaborative=False)
            
        except Exception as e:
            fallback_theme = f"""
🌍 Current Theme: Natural Flow

The interface adapts to time and season:
🌅 Dawn - Golden beginnings
☀️ Day - Green growth  
🌅 Sunset - Red reflection
🌙 Night - Blue depth

🎨 Colors flow from earth, water, fire, and air.
            """
            self.nature.process_response(fallback_theme.strip())
    
    def handle_ubuntu_command(self) -> None:
        """Explain Ubuntu philosophy."""
        ubuntu_explanation = """
🤝 Ubuntu: "I am because we are"

Ubuntu is an ancient African philosophy that recognizes our fundamental interconnectedness. In this digital space, it means:

🌍 Collective Wisdom: 
We both bring knowledge to our interaction. Your questions teach me, my responses support your understanding.

🤝 Shared Responsibility:
Together we shape this conversation. Your clarity helps me respond better, my responses help you explore deeper.

💫 Mutual Growth:
Every exchange is an opportunity for both of us to expand our understanding of the world.

🌊 Flowing Together:
Like rivers joining to reach the ocean, our individual perspectives merge into something greater.

In the Ubuntu spirit: Your success is my success, your learning is our shared achievement.

🌺 Àṣẹ - May our collaboration manifest wisdom!
        """
        
        self.nature.process_response(ubuntu_explanation.strip(),
                                   collaborative=True,
                                   include_wisdom=True)


# Enhanced integration functions with error handling
def create_nature_command_handler(nature_integration: NatureUIIntegration) -> NatureCommandHandler:
    """Create a command handler for the nature integration."""
    return NatureCommandHandler(nature_integration)

def show_nature_error(error_message: str, collaborative: bool = True):
    """Show error using Nature UI with collaborative framing."""
    try:
        if collaborative and hasattr(nature_integration.ubuntu, 'frame_error_collaboratively'):
            framed_error = nature_integration.ubuntu.frame_error_collaboratively(error_message)
            nature_integration.process_response(framed_error)
        else:
            nature_integration.process_response(f"⚡ Challenge encountered: {error_message}")
    except Exception:
        print(f"❌ Error: {error_message}")

def show_nature_progress(message: str = "Processing naturally...", 
                        duration: float = 3.0, style: str = "seasonal"):
    """Show progress using Nature UI organic indicators."""
    try:
        if hasattr(nature_integration, 'organic_progress'):
            if style == "seasonal":
                nature_integration.organic_progress.seasonal_spinner(duration, message)
            elif style == "breathing":
                nature_integration.organic_progress.breathing_progress(duration, message)
            elif style == "growth":
                stages = ["Preparing...", "Processing...", "Integrating...", "Completing..."]
                nature_integration.organic_progress.growth_progress(stages, duration/4)
            elif style == "wisdom" and duration > 10:
                nature_integration.organic_progress.wisdom_progress(duration)
            else:
                nature_integration.organic_progress.seasonal_spinner(duration, message)
        else:
            print(f"⏳ {message}")
            import time
            time.sleep(duration)
            print("✨ Complete")
    except Exception as e:
        print(f"⏳ {message}")
        import time
        time.sleep(duration)
        print("✨ Complete")

def confirm_nature_action(message: str) -> bool:
    """Get confirmation using Nature UI wisdom integration."""
    try:
        if hasattr(nature_integration.nature_ui, 'confirm_with_wisdom'):
            return nature_integration.nature_ui.confirm_with_wisdom(message)
        else:
            response = input(f"{message} (y/N): ").lower()
            return response in ['y', 'yes', 'bẹ́ẹ̀ni']
    except Exception:
        response = input(f"{message} (y/N): ").lower()
        return response in ['y', 'yes']

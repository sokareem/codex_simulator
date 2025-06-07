"""
Seasonal theme manager for Nature's Way UI
Automatically adjusts themes based on calendar seasons and local time
"""

import calendar
from datetime import datetime, date
from typing import Dict, List, Tuple
import json
from pathlib import Path

class SeasonalThemeManager:
    """Manages seasonal themes and time-aware UI adaptations."""
    
    def __init__(self):
        self.current_season = self._get_current_season()
        self.current_time_period = self._get_time_period()
        
        # Seasonal color palettes
        self.seasonal_palettes = {
            "winter": {
                "primary": "#6495ED",      # Cornflower blue
                "secondary": "#4682B4",    # Steel blue
                "accent": "#E6E6FA",       # Lavender
                "earth": "#696969",        # Dim gray
                "wisdom": "#9370DB",       # Medium purple
                "theme": "reflection_and_inner_growth"
            },
            "spring": {
                "primary": "#32CD32",      # Lime green
                "secondary": "#98FB98",    # Pale green
                "accent": "#FFB6C1",       # Light pink
                "earth": "#8FBC8F",        # Dark sea green
                "wisdom": "#DDA0DD",       # Plum
                "theme": "new_beginnings_and_growth"
            },
            "summer": {
                "primary": "#FFD700",      # Gold
                "secondary": "#FFA500",    # Orange
                "accent": "#87CEEB",       # Sky blue
                "earth": "#DAA520",        # Goldenrod
                "wisdom": "#FF6347",       # Tomato
                "theme": "abundance_and_energy"
            },
            "autumn": {
                "primary": "#CD853F",      # Peru
                "secondary": "#D2691E",    # Chocolate
                "accent": "#F4A460",       # Sandy brown
                "earth": "#A0522D",        # Sienna
                "wisdom": "#B22222",       # Fire brick
                "theme": "harvest_and_gratitude"
            }
        }
        
        # Seasonal wisdom and greetings
        self.seasonal_wisdom = {
            "winter": {
                "yoruba": "Àkókò òtútù",
                "english": "Time of reflection",
                "proverbs": [
                    ("Òtútù kì í pa ọmọ tó ní aṣọ", "Cold doesn't affect the child who has clothing - Preparation prevents problems"),
                    ("Àgbà tó bá gbójú lé òtútù á tú", "The elder who trusts in cold will be disappointed - Don't rely on harsh conditions")
                ],
                "energy": "contemplative",
                "symbols": ["❄️", "🌙", "⭐", "🕯️"]
            },
            "spring": {
                "yoruba": "Àkókò ìtànṣán",
                "english": "Time of new light",
                "proverbs": [
                    ("Òkú òwe là ń fi sọ̀rọ̀ ọ̀nà", "We use old proverbs to discuss new paths - Wisdom guides new beginnings"),
                    ("Epo tó bá dára á má kú nínú ìgò", "Good oil won't spoil in the container - Quality endures through seasons")
                ],
                "energy": "emerging",
                "symbols": ["🌱", "🌸", "🦋", "🌿"]
            },
            "summer": {
                "yoruba": "Àkókò ọ̀rọ̀",
                "english": "Time of abundance",
                "proverbs": [
                    ("Ọjọ́ ìrẹ̀ ni ti gbogbo wa", "Good days belong to us all - Abundance is meant to be shared"),
                    ("Àìmọ̀ràn ló pa Mariwo", "Lack of planning killed Mariwo - Even in abundance, wisdom is needed")
                ],
                "energy": "vibrant",
                "symbols": ["☀️", "🌻", "🍯", "🔥"]
            },
            "autumn": {
                "yoruba": "Àkókò ìkórè",
                "english": "Time of harvest",
                "proverbs": [
                    ("Èyí tí a bá gbìn ni à ń ká", "What we plant is what we harvest - Actions have consequences"),
                    ("Ọpẹ́ tó kó eso ló yẹ kí a mọ̀ lọ́wọ́", "The palm tree that bears fruit deserves our gratitude")
                ],
                "energy": "grateful",
                "symbols": ["🍂", "🍎", "🌾", "🦉"]
            }
        }
        
    def _get_current_season(self) -> str:
        """Determine current season based on date."""
        today = date.today()
        month = today.month
        
        # Northern hemisphere seasons (adjust for location if needed)
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:  # 9, 10, 11
            return "autumn"
    
    def _get_time_period(self) -> str:
        """Get current time period for daily adaptations."""
        hour = datetime.now().hour
        
        if 5 <= hour < 8:
            return "dawn"
        elif 8 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "sunset"
        else:
            return "night"
    
    def get_current_palette(self) -> Dict[str, str]:
        """Get the current color palette based on season and time."""
        base_palette = self.seasonal_palettes[self.current_season].copy()
        
        # Adjust brightness based on time of day
        time_adjustments = {
            "dawn": 0.8,      # Softer colors
            "morning": 1.0,   # Full brightness
            "afternoon": 1.0, # Full brightness
            "sunset": 0.9,    # Slightly muted
            "night": 0.6      # Much softer
        }
        
        adjustment = time_adjustments[self.current_time_period]
        
        # For now, return base palette (color adjustment would need hex manipulation)
        return base_palette
    
    def get_seasonal_greeting(self) -> str:
        """Get appropriate seasonal greeting."""
        season_data = self.seasonal_wisdom[self.current_season]
        
        greetings = {
            "winter": f"❄️ {season_data['yoruba']} - {season_data['english']}",
            "spring": f"🌸 {season_data['yoruba']} - {season_data['english']}",
            "summer": f"☀️ {season_data['yoruba']} - {season_data['english']}",
            "autumn": f"🍂 {season_data['yoruba']} - {season_data['english']}"
        }
        
        return greetings[self.current_season]
    
    def get_seasonal_wisdom(self) -> Tuple[str, str]:
        """Get random seasonal wisdom."""
        import random
        season_data = self.seasonal_wisdom[self.current_season]
        return random.choice(season_data['proverbs'])
    
    def get_seasonal_symbols(self) -> List[str]:
        """Get symbols representing current season."""
        return self.seasonal_wisdom[self.current_season]['symbols']
    
    def get_energy_level(self) -> str:
        """Get current energy recommendation based on season and time."""
        season_energy = self.seasonal_wisdom[self.current_season]['energy']
        
        time_energy = {
            "dawn": "gentle",
            "morning": "focused", 
            "afternoon": "active",
            "sunset": "reflective",
            "night": "restful"
        }
        
        return f"{season_energy}_{time_energy[self.current_time_period]}"
    
    def should_show_wisdom(self) -> bool:
        """Determine if wisdom should be shown based on natural timing."""
        # More wisdom during reflective times
        wisdom_probabilities = {
            "dawn": 0.4,
            "morning": 0.2,
            "afternoon": 0.1,
            "sunset": 0.5,
            "night": 0.3
        }
        
        import random
        return random.random() < wisdom_probabilities[self.current_time_period]
    
    def get_transition_message(self) -> str:
        """Get message for seasonal transitions."""
        today = date.today()
        
        # Check if we're near season transitions (within 3 days)
        season_starts = {
            "spring": (3, 20),  # March 20th
            "summer": (6, 21),  # June 21st  
            "autumn": (9, 22),  # September 22nd
            "winter": (12, 21)  # December 21st
        }
        
        for season, (month, day) in season_starts.items():
            season_date = date(today.year, month, day)
            days_until = (season_date - today).days
            
            if 0 <= days_until <= 3:
                return f"🌿 {season.title()} approaches in {days_until} days - prepare for seasonal energy shift"
        
        return ""

# Global instance
seasonal_manager = SeasonalThemeManager()

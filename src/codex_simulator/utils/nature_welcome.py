"""
Enhanced welcome experience integrating Nature's Way Philosophy with Yoruba wisdom
"""

import random
from datetime import datetime
from typing import Dict, List, Tuple

class NatureWelcome:
    """Creates contextual, culturally-aware welcome experiences."""
    
    def __init__(self):
        self.yoruba_greetings = {
            "morning": ["Kú àárọ̀", "Kú owúrọ̀", "Kú àkókò tó dára"],
            "afternoon": ["Kú àṣán", "Kú ọ̀sán", "Kú àkókò tó rẹ́"],  
            "evening": ["Kú alẹ́", "Kú ìrọ̀lẹ́", "Kú àṣálẹ́"]
        }
        
        self.nature_wisdom = [
            ("🌊", "Like water, let your thoughts flow naturally"),
            ("🌱", "Every great oak was once an acorn that held its ground"),
            ("🌸", "In the garden of the mind, cultivate wisdom"),
            ("🦋", "Transformation is nature's greatest teaching"),
            ("🌍", "We are all connected in the web of existence")
        ]
        
        self.yoruba_proverbs_contextual = {
            "work": ("Iṣẹ́ ní ò̩ògùn ìṣẹ́", "Work is the medicine for poverty"),
            "patience": ("Ẹni tó bá ní sùúrù á jeun ẹyọ àgbon", "One who has patience will eat the coconut kernel"),
            "wisdom": ("Ọgbọ́n ju agbára lọ", "Wisdom is greater than strength"),
            "unity": ("Ọwọ́ kan ò gb'òkú ní agbon", "One hand cannot lift a coconut - unity is strength"),
            "learning": ("Kò sí ọjọ́ tó tó kéji ọjọ́ ìbímọ", "No day is as good as the day of gaining knowledge")
        }
    
    def get_time_greeting(self) -> Tuple[str, str]:
        """Get appropriate greeting based on time of day."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            yoruba = random.choice(self.yoruba_greetings["morning"])
            english = "Good morning"
            blessing = "May your day flow like gentle streams"
        elif 12 <= hour < 17:
            yoruba = random.choice(self.yoruba_greetings["afternoon"])
            english = "Good afternoon"  
            blessing = "May the sun energize your endeavors"
        else:
            yoruba = random.choice(self.yoruba_greetings["evening"])
            english = "Good evening"
            blessing = "May wisdom settle like evening dew"
            
        return f"{yoruba}, Sinmi! {english}.", blessing
    
    def get_seasonal_message(self) -> str:
        """Get seasonal message aligned with natural cycles."""
        month = datetime.now().month
        
        seasonal_messages = {
            "winter": "🌙 In winter's reflection, we find inner strength - Àkókò òtútù",
            "spring": "🌸 Spring brings new possibilities - Àkókò ìtànṣán", 
            "summer": "☀️ Summer's abundance flows through all we do - Àkókò ọ̀rọ̀",
            "autumn": "🍂 Harvest time teaches us gratitude - Àkókò ìkórè"
        }
        
        if month in [12, 1, 2]:
            return seasonal_messages["winter"]
        elif month in [3, 4, 5]:
            return seasonal_messages["spring"]
        elif month in [6, 7, 8]:
            return seasonal_messages["summer"]
        else:
            return seasonal_messages["autumn"]
    
    def get_contextual_wisdom(self, context: str = "general") -> Tuple[str, str]:
        """Get contextual Yoruba wisdom for the situation."""
        if context in self.yoruba_proverbs_contextual:
            yoruba, english = self.yoruba_proverbs_contextual[context]
        else:
            # Random nature wisdom
            symbol, wisdom = random.choice(self.nature_wisdom)
            yoruba = f"{symbol} Àṣẹ"
            english = wisdom
            
        return yoruba, english
    
    def create_personalized_welcome(self, user_name: str = "Sinmi", context: str = "general") -> Dict[str, str]:
        """Create a complete personalized welcome experience."""
        greeting, blessing = self.get_time_greeting()
        seasonal = self.get_seasonal_message()
        wisdom_yoruba, wisdom_english = self.get_contextual_wisdom(context)
        
        # Create flowing, natural welcome
        welcome_parts = {
            "greeting": greeting,
            "blessing": blessing,
            "seasonal": seasonal,
            "wisdom_yoruba": wisdom_yoruba,
            "wisdom_english": wisdom_english,
            "connection": "🌿 Ready to explore the digital forest together?",
            "invitation": "What flows through your mind today?"
        }
        
        return welcome_parts

# Helper function for integration
def create_nature_welcome(user_name: str = "Sinmi", context: str = "general") -> str:
    """Create a flowing, natural welcome message."""
    welcome = NatureWelcome()
    parts = welcome.create_personalized_welcome(user_name, context)
    
    # Compose flowing message
    message = f"""
{parts['greeting']}

{parts['blessing']}

{parts['seasonal']}

💫 {parts['wisdom_yoruba']}
   {parts['wisdom_english']}

{parts['connection']}
{parts['invitation']}

Àṣẹ - May your commands manifest with power! 🌟
"""
    
    return message.strip()

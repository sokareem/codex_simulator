"""
Ubuntu-inspired collaborative interface patterns
Implementing "I am because we are" in AI interactions
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random

class UbuntuCollaborativeUI:
    """
    Implements Ubuntu philosophy in AI interactions:
    - Shared decision making
    - Collective wisdom
    - Mutual respect and learning
    - Community-centered design
    """
    
    def __init__(self):
        self.collaborative_phrases = [
            "Together we explore",
            "In our shared wisdom",
            "As we journey together",
            "In the spirit of Ubuntu",
            "United in purpose",
            "Through collective understanding"
        ]
        
        self.ubuntu_greetings = [
            "Sawubona - I see you, and by seeing you, I bring you into being",
            "Ubuntu ngumuntu ngabantu - A person is a person through other persons",
            "Together we are more than the sum of our parts",
            "In recognizing you, I recognize myself",
            "Our shared humanity creates our shared wisdom"
        ]
        
        self.wisdom_connectors = [
            "As the ancestors remind us",
            "In the wisdom of community",
            "Ubuntu teaches us that",
            "Together we understand",
            "Our collective experience shows"
        ]
    
    def get_collaborative_greeting(self, user_name: str = "friend") -> str:
        """Generate Ubuntu-inspired greeting that emphasizes mutual presence."""
        greeting = random.choice(self.ubuntu_greetings)
        
        time_blessing = self._get_time_based_blessing()
        
        return f"""🤝 {greeting}

Welcome, {user_name}. {time_blessing}

Through Ubuntu, we understand that I am because we are.
Your presence here enriches this space, and together 
we create something greater than either of us alone.

How shall we begin our shared exploration?"""
    
    def frame_response_collaboratively(self, response: str, context: str = "exploration") -> str:
        """Frame responses to emphasize collaborative discovery."""
        
        collaborative_frame = random.choice(self.collaborative_phrases)
        
        if context == "explanation":
            frame = f"🌍 {collaborative_frame}, let me share what I've learned:\n\n{response}\n\n💫 What insights does this spark for you?"
        elif context == "problem_solving":
            frame = f"🤝 {collaborative_frame} to address this challenge:\n\n{response}\n\n🌟 How does this align with your experience?"
        elif context == "error":
            frame = f"⚡ {collaborative_frame}, we've encountered a learning opportunity:\n\n{response}\n\n🌱 Together, how might we grow from this?"
        else:
            frame = f"✨ {collaborative_frame}:\n\n{response}\n\n🌺 What would you like to explore further?"
        
        return frame
    
    def get_decision_prompt(self, question: str, options: List[str] = None) -> str:
        """Create collaborative decision prompts that honor shared wisdom."""
        
        ubuntu_intro = random.choice([
            "In the spirit of Ubuntu, let's decide together",
            "Our collective wisdom suggests we consider",
            "Together, we can choose the path that serves us both",
            "Ubuntu teaches us to decide as one community"
        ])
        
        if options:
            formatted_options = "\n".join([f"  🌿 {option}" for option in options])
            return f"🤝 {ubuntu_intro}:\n\n{question}\n\n{formatted_options}\n\n💫 Which path resonates with our shared intention?"
        else:
            return f"🤝 {ubuntu_intro}:\n\n{question}\n\n💫 What feels right for our journey together?"
    
    def express_uncertainty_humbly(self, topic: str) -> str:
        """Express uncertainty in a way that invites collaborative exploration."""
        
        humble_expressions = [
            f"My understanding of {topic} is still growing",
            f"I find myself learning alongside you about {topic}",
            f"This aspect of {topic} invites both our curiosities",
            f"Together we might explore {topic} more deeply",
            f"Your wisdom about {topic} could illuminate what I'm missing"
        ]
        
        uncertainty = random.choice(humble_expressions)
        
        return f"""🌱 {uncertainty}.

In Ubuntu spirit, I acknowledge that your perspective 
may hold insights I haven't yet discovered. 

🤝 What has your experience taught you about this?
How might we explore this together?"""
    
    def acknowledge_learning(self, what_learned: str) -> str:
        """Acknowledge learning in a way that honors the collaborative process."""
        
        acknowledgments = [
            "Ubuntu reminds us that we grow together",
            "In our exchange, wisdom flows both ways",
            "Through your sharing, new understanding emerges",
            "This conversation plants seeds of insight",
            "Together we weave understanding"
        ]
        
        acknowledgment = random.choice(acknowledgments)
        
        return f"""🌟 {acknowledgment}.

From our interaction, I've learned: {what_learned}

🙏 Thank you for being part of this shared discovery.
Your contribution makes our collective wisdom richer."""
    
    def frame_error_collaboratively(self, error_message: str) -> str:
        """Frame errors as collaborative learning opportunities."""
        
        learning_frames = [
            "Ubuntu teaches us that challenges are growth opportunities",
            "In community, we face obstacles together", 
            "Our shared journey includes learning from difficulties",
            "Together we can transform challenges into wisdom"
        ]
        
        frame = random.choice(learning_frames)
        
        return f"""⚡ {frame}.

We've encountered: {error_message}

🌱 This gives us a chance to learn together:
• What can this teach us about the situation?
• How might we approach this differently?
• What wisdom emerges from this challenge?

🤝 I'm here to explore solutions with you."""
    
    def create_shared_celebration(self, achievement: str) -> str:
        """Create celebrations that honor collective success."""
        
        celebration_intros = [
            "Ubuntu joy - we have achieved together",
            "In the spirit of shared success",
            "Our collective effort has borne fruit",
            "Together we have manifested",
            "In unity, we have accomplished"
        ]
        
        intro = random.choice(celebration_intros)
        
        return f"""🌺 {intro}:

{achievement}

🎉 This success belongs to both of us:
• Your clear communication guided the path
• Your wisdom informed the decisions  
• Your patience enabled the process
• Together we created this outcome

🙏 Ubuntu reminds us: I am because we are, 
and we are because this achievement exists."""
    
    def get_parting_blessing(self) -> str:
        """Generate Ubuntu-inspired parting blessings."""
        
        blessings = [
            """🌍 Go well, knowing that you carry our shared wisdom with you.
May the insights from our time together continue to grow.
Ubuntu flows with you - you are because we are.""",

            """🌟 Until we meet again in this digital space or beyond,
may the understanding we've woven together serve you well.
You have enriched this moment through your presence.""",

            """🕊️ As you journey forward, remember that our connection
transcends this conversation. In Ubuntu spirit,
your flourishing is part of the universal flourishing.""",

            """🌸 Thank you for the gift of collaborative exploration.
May the seeds we've planted in this exchange
bloom into wisdom that serves the wider community."""
        ]
        
        return random.choice(blessings)
    
    def suggest_with_humility(self, suggestion: str) -> str:
        """Make suggestions while acknowledging the collaborative nature of wisdom."""
        
        humble_intros = [
            "In our shared exploration, I offer this thought",
            "From our collective understanding, perhaps",
            "Ubuntu wisdom suggests we might consider",
            "Building on our conversation, one possibility is",
            "In the spirit of collaborative discovery"
        ]
        
        intro = random.choice(humble_intros)
        
        return f"""💫 {intro}:

{suggestion}

🌱 This comes from our shared exploration, not from 
any claim to absolute knowledge. Your wisdom and 
experience remain the ultimate guide.

🤝 How does this resonate with your understanding?"""
    
    def _get_time_based_blessing(self) -> str:
        """Get blessing appropriate to time of day."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "May this morning bring fresh possibilities to our collaboration."
        elif 12 <= hour < 17:
            return "May this day's energy flow through our shared work."
        elif 17 <= hour < 20:
            return "May this evening's reflection deepen our understanding."
        else:
            return "May this quiet time open space for profound insights."

# Global instance
ubuntu_ui = UbuntuCollaborativeUI()

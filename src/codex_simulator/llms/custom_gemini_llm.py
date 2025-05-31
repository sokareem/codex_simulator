"""
Custom Gemini LLM integration for CodexSimulator.
Provides a simplified interface that avoids LangChain compatibility issues.
"""

import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


class CustomGeminiLLM:
    """
    Custom Gemini LLM that works independently of LangChain compatibility issues.
    Simplified implementation that focuses on core functionality.
    """
    
    def __init__(self, 
                 model_name: str = "gemini-1.5-flash",
                 api_key: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None):
        
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai is required but not installed")
        
        # Get API key
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set")
        
        # Configure the client
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Safety settings - less restrictive for coding tasks
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    def invoke(self, prompt: str) -> "AIMessage":
        """
        Invoke the model with a prompt and return an AIMessage-like object.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Return a simple response object
            return AIMessage(content=response.text)
            
        except Exception as e:
            return AIMessage(content=f"Error generating response: {str(e)}")
    
    def generate(self, messages: List[Dict[str, str]]) -> "AIMessage":
        """
        Generate response from a list of messages (for chat-like interface).
        """
        # Convert messages to a single prompt
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n".join(prompt_parts)
        return self.invoke(prompt)
    
    def stream(self, prompt: str):
        """
        Stream the response (simplified implementation).
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield AIMessage(content=chunk.text)
                    
        except Exception as e:
            yield AIMessage(content=f"Error in streaming: {str(e)}")


class AIMessage:
    """Simple AIMessage-like class to avoid LangChain dependencies."""
    
    def __init__(self, content: str):
        self.content = content
        
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f"AIMessage(content='{self.content[:50]}...')"


# For backwards compatibility
class CustomGeminiChatModel(CustomGeminiLLM):
    """Alias for CustomGeminiLLM for backwards compatibility."""
    pass


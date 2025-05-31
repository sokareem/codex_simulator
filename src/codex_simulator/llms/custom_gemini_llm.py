import os
from typing import Any, List, Mapping, Optional

import google.generativeai as genai_sdk # Renamed to avoid conflict
from google.generativeai.types import GenerationConfig
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from pydantic.v1 import Field, root_validator # Updated import for Pydantic v1 compatibility

class CustomGeminiLLM(LLM):
    """
    Custom LangChain LLM wrapper for Google Gemini API using the google-generativeai client.
    It uses the `generate_content` method.
    """
    
    model: str # Renamed from model_name, no alias
    temperature: float = 0.7
    google_api_key: str # Made a standard required field

    client: Any = Field(default=None, exclude=True) # Stores the genai.GenerativeModel instance

    @root_validator() # Runs after individual field validation
    def validate_environment_and_setup_client(cls, values: dict) -> dict:
        """Validate that api key and python package exists in environment and setup client."""
        api_key = values.get("google_api_key")
        model_name = values.get("model")

        if not api_key:
            # This should ideally be caught by Pydantic if google_api_key is required and not provided.
            # Adding an explicit check here for robustness.
            raise ValueError(
                "Google API Key not provided. It's a required field for CustomGeminiLLM."
            )
        
        if not model_name:
            raise ValueError(
                "Model name not provided. It's a required field for CustomGeminiLLM."
            )
        
        try:
            # google.generativeai was already imported as genai_sdk
            pass
        except ImportError: # Should not happen if import at top level succeeded
            raise ImportError(
                "Could not import google-generativeai python package. "
                "Please install it with `pip install google-generativeai`."
            )
        
        genai_sdk.configure(api_key=api_key)
        values["client"] = genai_sdk.GenerativeModel(model_name=model_name)
        return values

    @property
    def _llm_type(self) -> str:
        return "custom_gemini_via_google_sdk"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call out to Gemini's generate_content method.
        """
        generation_config_params = {"temperature": self.temperature}
        
        if "temperature" in kwargs: # Allow overriding temperature
            generation_config_params["temperature"] = kwargs.pop("temperature")
        
        # Handle stop sequences if provided and supported by the config
        # The google-generativeai SDK's GenerationConfig takes 'stop_sequences'
        if stop is not None:
            generation_config_params["stop_sequences"] = stop
            
        generation_config = GenerationConfig(**generation_config_params)

        try:
            response = self.client.generate_content(
                contents=prompt,
                generation_config=generation_config,
                **kwargs 
            )
            
            if response.text:
                return response.text
            elif response.parts:
                full_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                if full_text:
                    return full_text
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    return f"Error: Content generation blocked. Reason: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
            
            if response.candidates:
                candidate_text_parts = []
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part_in_candidate in candidate.content.parts: # Renamed inner loop variable
                            if hasattr(part_in_candidate, 'text'):
                                candidate_text_parts.append(part_in_candidate.text)
                if candidate_text_parts:
                    return "".join(candidate_text_parts)

            return "Error: Empty response from Gemini API or content blocked."

        except Exception as e:
            return f"Error generating content with Gemini: {e}"


    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": self.model, "temperature": self.temperature}

    @property
    def supports_stop_words(self) -> bool:
        """Whether this LLM supports stop words."""
        return True # Gemini API supports stop sequences


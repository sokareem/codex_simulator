import os
import json
import requests
from typing import Dict, Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SerpAPIToolInput(BaseModel):
    """Input for SerpAPITool."""
    query: str = Field(..., description="The search query to be executed")

class SerpAPITool(BaseTool):
    """Tool for performing web searches using Brave Search API."""
    name: str = "serp_api_tool"
    description: str = "Search the web for current information on a given topic. Useful for finding up-to-date information."
    args_schema: Type[BaseModel] = SerpAPIToolInput
    
    # Define these as class fields to avoid Pydantic errors
    api_key: Optional[str] = None
    api_base_url: str = "https://api.search.brave.com/res/v1/web/search"  # Brave Search API endpoint
    
    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("BRAVE_API_KEY") or os.getenv("SERPER_API_KEY")
        
        if api_base_url:
            self.api_base_url = api_base_url
            
        # Check for API key
        if not self.api_key:
            raise ValueError("No API key found. Set BRAVE_API_KEY environment variable.")

    def _run(self, query: str) -> str:
        """Execute a web search for the given query."""
        try:
            # Parse the input (which might be a JSON string)
            if isinstance(query, str) and query.startswith("{"):
                try:
                    query_data = json.loads(query)
                    query = query_data.get("query", query)
                except json.JSONDecodeError:
                    pass  # Use the original query if it's not valid JSON
            
            # Log what we're about to do
            print(f"Performing web search for: '{query}'")
            print(f"Using API endpoint: {self.api_base_url}")
                    
            # Set up headers for Brave Search API
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            # Query parameters for Brave Search
            params = {
                "q": query,
                "count": 5,  # Limit to 5 results
                "country": "US",
                "search_lang": "en"
            }
            
            # Make the request to Brave Search API
            response = requests.get(
                self.api_base_url, 
                headers=headers,
                params=params,
                timeout=30
            )
            
            # Debug information
            print(f"API Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                search_results = response.json()
                
                # Format results into a readable string
                formatted_results = f"Web search results for '{query}':\n\n"
                
                # Process web search results from Brave Search API
                if "web" in search_results and "results" in search_results["web"]:
                    for i, result in enumerate(search_results["web"]["results"][:5]):
                        title = result.get("title", "No title")
                        link = result.get("url", "No link")
                        description = result.get("description", "No description")
                        formatted_results += f"{i+1}. {title}\n   {link}\n   {description}\n\n"
                else:
                    formatted_results += "No web search results found.\n\n"
                
                # Include featured snippet if available
                if "featured_snippet" in search_results and search_results["featured_snippet"]:
                    snippet = search_results["featured_snippet"]
                    formatted_results += f"Featured Snippet: {snippet.get('title', '')}\n{snippet.get('description', '')}\n\n"
                
                return formatted_results
            else:
                # Attempt to check if it's a misconfiguration
                error_msg = f"Error performing web search: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {json.dumps(error_detail)}"
                except:
                    error_msg += f" - {response.text}"
                
                # Add some troubleshooting guidance
                error_msg += "\n\nTroubleshooting suggestions:"
                error_msg += "\n1. Verify your BRAVE_API_KEY in the .env file"
                error_msg += "\n2. Ensure your Brave Search API subscription is active"
                error_msg += "\n3. Check if you've reached your API usage limits"
                
                return error_msg
                
        except requests.RequestException as e:
            return f"Web search error: {str(e)}\n\nFallback: Please try using an alternative search method or check your internet connection."

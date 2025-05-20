import os
import requests
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SerpAPIToolInput(BaseModel):
    query: str = Field(..., description="The search query to perform.")

class SerpAPITool(BaseTool):
    """A tool to search the web using Langsearch API.
    
    This tool sends search queries to Langsearch API and formats the results.
    It requires a Langsearch API key set in the LANGSEARCH_API_KEY environment variable.
    """
    name: str = "serp_api_tool"
    description: str = "Performs web searches using Langsearch API to find relevant information."
    args_schema: Type[BaseModel] = SerpAPIToolInput

    # Define all fields that we'll use
    langsearch_api_url: str = "https://api.langsearch.ai/v1"
    api_key: Optional[str] = None
    
    def __init__(self, langsearch_api_key: Optional[str] = None, langsearch_api_url: Optional[str] = None, **kwargs):
        # Set up kwargs dictionary with all our parameters
        kwargs["langsearch_api_url"] = langsearch_api_url or os.getenv("LANGSEARCH_API_URL") or "https://api.langsearch.ai/v1"
        kwargs["api_key"] = langsearch_api_key or os.getenv("LANGSEARCH_API_KEY")
        
        super().__init__(**kwargs)

    def _run(self, query: str) -> str:
        """Run the search query via Langsearch API."""
        if not self.api_key:
            return f"Web search results for '{query}':\n\nError: Langsearch API key not provided. Set the LANGSEARCH_API_KEY environment variable."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare the Langsearch API request payload
        payload = {
            "query": query,
            "max_results": 5,  # Limiting to 5 results
            "use_cache": True  # Use cached results when available for better performance
        }
        
        try:
            response = requests.post(
                f"{self.langsearch_api_url}/search",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"Web search results for '{query}':\n\nSearch API returned status code {response.status_code}"

            results = response.json()
            return self._format_search_results(results, query)

        except Exception as e:
            return f"Web search results for '{query}':\n\nError performing web search: {e}"

    def _format_search_results(self, results: Dict[str, Any], query: str) -> str:
        """Format Langsearch API results into readable text."""
        output = f"Web search results for '{query}':\n\n"
        
        # Parse Langsearch results
        if "results" in results and results["results"]:
            for i, result in enumerate(results["results"], 1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                snippet = result.get("snippet", "No description available")
                
                # Format each result
                output += f"{i}. {title}\n"
                output += f"   URL: {url}\n"
                output += f"   Description: {snippet}\n\n"
                
            # Add metadata if available
            if "metadata" in results:
                if "total_results" in results["metadata"]:
                    output += f"Total results found: {results['metadata']['total_results']}\n"
                if "search_time" in results["metadata"]:
                    output += f"Search completed in {results['metadata']['search_time']} seconds\n"
        else:
            output += "No search results available.\n\n"
            
        return output.strip()

import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from bs4 import BeautifulSoup

class WebsiteToolInput(BaseModel):
    """Input for the WebsiteTool."""
    url: str = Field(..., description="The website URL to fetch and analyze.")

class WebsiteTool(BaseTool):
    """A tool to fetch and analyze website content."""
    name: str = "website_tool"
    description: str = "Fetches content from a specific website URL for information gathering."
    args_schema: Type[BaseModel] = WebsiteToolInput

    def _run(self, url: str) -> str:
        """Fetch and process content from the provided URL."""
        try:
            # Basic safety check for URL
            if not (url.startswith("http://") or url.startswith("https://")):
                return f"Error: Invalid URL format. URLs must begin with http:// or https://"
            
            # Make the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return f"Error: Could not fetch content from {url}. Status code: {response.status_code}"
            
            # Parse content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length
            max_length = 5000  # Characters
            if len(text) > max_length:
                text = text[:max_length] + "...\n[Content truncated due to length]"
            
            return f"Content from {url}:\n\n{text}"
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching website: {str(e)}"
        except Exception as e:
            return f"Error processing website content: {str(e)}"

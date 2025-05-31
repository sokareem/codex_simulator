#!/usr/bin/env python
import os
import sys
import dotenv
import json
import requests
from codex_simulator.tools.serp_api_tool import SerpAPITool

# Load environment variables
dotenv.load_dotenv()

def test_search(query):
    """Test the search functionality with a given query."""
    print(f"Testing search with query: '{query}'")
    
    # Try with SerpAPITool
    try:
        print("\n1. Testing with SerpAPITool class using Brave Search")
        print("-" * 50)
        
        # Create the search tool
        search_tool = SerpAPITool()
        
        # Execute the search
        result = search_tool._run(query)
        
        # Print the result
        print("\nSearch Results:")
        print("-" * 50)
        print(result)
        print("-" * 50)
    except Exception as e:
        print(f"Error using SerpAPITool: {e}")
    
    # Try direct API call
    try:
        print("\n2. Testing with direct API call to Brave Search")
        print("-" * 50)
        
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            print("No BRAVE_API_KEY found in environment variables")
            return False
            
        endpoint = "https://api.search.brave.com/res/v1/web/search"
        
        print(f"Trying endpoint: {endpoint}")
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": 5,
            "country": "US",
            "search_lang": "en"
        }
        
        response = requests.get(
            endpoint, 
            headers=headers,
            params=params,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Brave Search API endpoint works")
            print(f"Response preview: {str(response.text)[:200]}...")
            return True
        else:
            print(f"Failed with: {response.text[:200]}")
            print("\nAPI call failed. Please check your API key and account status.")
            return False
        
    except Exception as e:
        print(f"Error during direct API test: {e}")
        return False

if __name__ == "__main__":
    # Use command line argument if provided, otherwise use a default query
    query = sys.argv[1] if len(sys.argv) > 1 else "current AI developments"
    test_search(query)

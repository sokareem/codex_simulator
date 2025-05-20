import os
import unittest
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock

from codex_simulator.tools.serp_api_tool import SerpAPITool, SerpAPIToolInput

class TestWebSearchTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # load .env if you want to override API settings
        load_dotenv()

    @patch('requests.post')
    def test_simple_web_query(self, mock_post):
        """
        Test a simple web query using the SerpAPITool with mocked API response.
        """
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "CrewAI: A framework for creating AI agents",
                    "url": "https://github.com/crewai/crewai",
                    "snippet": "CrewAI is a framework for orchestrating role-playing, autonomous AI agents."
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Create tool with mock API key
        tool = SerpAPITool(langsearch_api_key="mock_api_key")  
        query = "What is CrewAI?"
        print(f"\nPerforming web search for: \"{query}\"")
        
        result = tool._run(query=query)

        print("\nSearch Result:")
        print(result)

        # Verify mock was called correctly
        mock_post.assert_called_once()
        
        # Check response formatting
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn(f"Web search results for '{query}'", result)
        self.assertIn("CrewAI", result)  # Should be in the mocked response
        self.assertNotIn("Error:", result.split("\n\n",1)[0])  # header should be clean

    def test_missing_api_key(self):
        """
        Test that the tool returns an appropriate message when API key is missing.
        """
        # Temporarily unset API key
        original_api_key = os.environ.pop("LANGSEARCH_API_KEY", None)
        
        tool = SerpAPITool()  # No API key provided
        query = "Test query without API key"
        
        result = tool._run(query=query)
        
        print("\nSearch Result (No API Key):")
        print(result)
        
        self.assertIn("Langsearch API key not provided", result)
        
        # Restore API key if it was originally set
        if original_api_key:
            os.environ["LANGSEARCH_API_KEY"] = original_api_key

if __name__ == '__main__':
    unittest.main()

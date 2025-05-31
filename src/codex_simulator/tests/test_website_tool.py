import unittest
from unittest.mock import patch, MagicMock
import requests

from codex_simulator.tools.website_tool import WebsiteTool, WebsiteToolInput

class TestWebsiteTool(unittest.TestCase):

    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_fetch_website_content_success(self, mock_beautiful_soup, mock_requests_get):
        tool = WebsiteTool()

        # Mock requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><title>Test Page</title></head><body><p>Hello World</p></body></html>"
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup_instance = MagicMock()
        mock_soup_instance.title.string = "Test Page"
        mock_soup_instance.get_text.return_value = "Test Page Hello World"
        mock_beautiful_soup.return_value = mock_soup_instance

        url = "http://example.com"
        result = tool._run(url=url)

        self.assertIn("Title: Test Page", result)
        self.assertIn("Content Snippet (first 500 chars):", result)
        self.assertIn("Test Page Hello World", result)
        mock_requests_get.assert_called_once_with(url, timeout=10)
        mock_beautiful_soup.assert_called_once_with(mock_response.text, 'html.parser')

    @patch('requests.get')
    def test_fetch_website_http_error(self, mock_requests_get):
        tool = WebsiteTool()

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_requests_get.return_value = mock_response
        
        url = "http://example.com/notfound"
        result = tool._run(url=url)

        self.assertIn(f"Error fetching URL {url}: 404 Client Error", result)

    @patch('requests.get')
    def test_fetch_website_request_exception(self, mock_requests_get):
        tool = WebsiteTool()
        mock_requests_get.side_effect = requests.exceptions.RequestException("Connection error")

        url = "http://example.com/timeout"
        result = tool._run(url=url)
        self.assertIn(f"Error fetching URL {url}: Connection error", result)

    def test_invalid_url_input(self):
        tool = WebsiteTool()
        # The tool's _run method expects a 'url' kwarg due to Pydantic model.
        # If called directly with positional arg, it might fail differently or Pydantic handles it.
        # Let's test with invalid URL format.
        # Pydantic validation for URL format is not part of the default WebsiteToolInput.
        # The tool itself doesn't validate URL format before passing to requests.get.
        # So, this test will likely pass through to requests.get which would raise an error.
        with patch('requests.get', side_effect=requests.exceptions.InvalidURL("Invalid URL")):
            result = tool._run(url="not_a_valid_url")
            self.assertIn("Error fetching URL not_a_valid_url: Invalid URL", result)


if __name__ == '__main__':
    unittest.main()

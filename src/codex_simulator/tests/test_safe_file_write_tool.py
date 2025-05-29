import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

from codex_simulator.tools.safe_file_write_tool import SafeFileWriteTool

class TestSafeFileWriteTool(unittest.TestCase):

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.path.isdir', return_value=False) # Target is not a directory
    @patch('codex_simulator.utils.permission_manager.PermissionManager.request_permission', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_write_new_file_success(self, mock_file_open, mock_request_permission, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileWriteTool(allowed_files=["new_file.txt"]) # Allow this specific file
        
        mock_abspath.return_value = "/abs/path/to/new_file.txt"
        mock_expanduser.side_effect = lambda x: x
        mock_exists.return_value = False # File does not exist yet

        result = tool._run(file_path="new_file.txt", content="Hello World", append=False)
        
        self.assertEqual(result, "Successfully wrote to file: /abs/path/to/new_file.txt")
        mock_request_permission.assert_called_once_with("write", "/abs/path/to/new_file.txt")
        mock_file_open.assert_called_once_with("/abs/path/to/new_file.txt", "w", encoding="utf-8")
        mock_file_open().write.assert_called_once_with("Hello World")

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('os.path.exists', return_value=True) # File exists
    @patch('os.path.isdir', return_value=False)
    @patch('codex_simulator.utils.permission_manager.PermissionManager.request_permission', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_append_to_existing_file_success(self, mock_file_open, mock_request_permission, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileWriteTool(allowed_files=["existing.txt"])
        
        mock_abspath.return_value = "/abs/path/to/existing.txt"
        mock_expanduser.side_effect = lambda x: x

        result = tool._run(file_path="existing.txt", content="More content", append=True)
        
        self.assertEqual(result, "Successfully appended to file: /abs/path/to/existing.txt")
        mock_request_permission.assert_called_once_with("append", "/abs/path/to/existing.txt")
        mock_file_open.assert_called_once_with("/abs/path/to/existing.txt", "a", encoding="utf-8")
        mock_file_open().write.assert_called_once_with("More content")

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('codex_simulator.utils.permission_manager.PermissionManager.request_permission', return_value=False) # Permission denied
    def test_write_permission_denied(self, mock_request_permission, mock_expanduser, mock_abspath):
        tool = SafeFileWriteTool(allowed_files=["any_file.txt"])
        mock_abspath.return_value = "/abs/path/to/any_file.txt"
        mock_expanduser.side_effect = lambda x: x

        result = tool._run(file_path="any_file.txt", content="test", append=False)
        self.assertEqual(result, "Error: Permission denied by user to write to /abs/path/to/any_file.txt.")

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    def test_write_to_blocked_file_by_pattern(self, mock_expanduser, mock_abspath):
        tool = SafeFileWriteTool(blocked_file_patterns=[r"\.env$", "credentials"], allowed_files=[])
        mock_abspath.return_value = "/abs/path/to/.env"
        mock_expanduser.side_effect = lambda x: x
        
        result = tool._run(file_path=".env", content="SECRET_KEY=123", append=False)
        self.assertIn("Error: Writing to file matching pattern", result)
        self.assertIn("is blocked for security reasons.", result)

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    def test_write_to_not_explicitly_allowed_file(self, mock_expanduser, mock_abspath):
        # If allowed_files is provided and non-empty, only those are allowed.
        tool = SafeFileWriteTool(allowed_files=["specific_safe.txt"])
        mock_abspath.return_value = "/abs/path/to/other_file.txt"
        mock_expanduser.side_effect = lambda x: x

        result = tool._run(file_path="other_file.txt", content="content", append=False)
        self.assertIn("Error: Writing to '/abs/path/to/other_file.txt' is not allowed. Allowed files/patterns:", result)


    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True) # Target is a directory
    @patch('codex_simulator.utils.permission_manager.PermissionManager.request_permission', return_value=True)
    def test_write_to_path_that_is_directory(self, mock_request_permission, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileWriteTool(allowed_files=["a_directory"]) # Allow writing to path named 'a_directory'
        mock_abspath.return_value = "/abs/path/to/a_directory"
        mock_expanduser.side_effect = lambda x: x

        result = tool._run(file_path="a_directory", content="test", append=False)
        self.assertEqual(result, "Error: Path '/abs/path/to/a_directory' is a directory, cannot write to it as a file.")


if __name__ == '__main__':
    unittest.main()

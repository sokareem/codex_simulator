import unittest
from unittest.mock import patch, mock_open, MagicMock
import os

from codex_simulator.tools.safe_file_read_tool import SafeFileReadTool

class TestSafeFileReadTool(unittest.TestCase):

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.path.isdir')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    def test_read_allowed_file_success(self, mock_file_open, mock_getsize, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileReadTool()
        
        mock_abspath.return_value = "/abs/path/to/file.txt"
        mock_expanduser.side_effect = lambda x: x
        mock_exists.return_value = True
        mock_isdir.return_value = False # It's a file
        mock_getsize.return_value = 100 # Less than max_file_size

        result = tool._run(file_path="file.txt")
        
        self.assertIn("Contents of file 'file.txt':", result)
        self.assertIn("file content", result)
        mock_file_open.assert_called_once_with("/abs/path/to/file.txt", "r", encoding="utf-8")

    def test_read_blocked_file(self):
        tool = SafeFileReadTool(blocked_files=["secret.txt"])
        with patch('os.path.abspath', return_value="/abs/path/to/secret.txt"), \
             patch('os.path.expanduser', side_effect=lambda x: x):
            result = tool._run(file_path="secret.txt")
            self.assertIn("Error: Access to 'secret.txt' files is restricted for security reasons", result)

    @patch('os.path.abspath', return_value="/abs/path/to/non_existent.txt")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=False)
    def test_read_non_existent_file(self, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileReadTool()
        result = tool._run(file_path="non_existent.txt")
        self.assertIn("Error: File '/abs/path/to/non_existent.txt' does not exist", result)

    @patch('os.path.abspath', return_value="/abs/path/to/a_directory")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True) # Path is a directory
    def test_read_path_is_directory(self, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileReadTool()
        result = tool._run(file_path="a_directory")
        self.assertIn("Error: Path '/abs/path/to/a_directory' is a directory, not a file. Use the directory tool instead.", result)

    @patch('os.path.abspath', return_value="/abs/path/to/large_file.txt")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    @patch('os.path.getsize')
    def test_read_file_too_large(self, mock_getsize, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileReadTool(max_file_size=1024) # 1KB limit for test
        mock_getsize.return_value = 2048 # File is 2KB

        result = tool._run(file_path="large_file.txt")
        self.assertIn("Error: File '/abs/path/to/large_file.txt' exceeds the maximum allowed size", result)

    @patch('os.path.abspath', return_value="/abs/path/to/file.txt")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False)
    @patch('os.path.getsize', return_value=100)
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_read_permission_error(self, mock_open, mock_getsize, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeFileReadTool()
        result = tool._run(file_path="file.txt")
        self.assertIn("Error: Permission denied to access file 'file.txt'.", result)


if __name__ == '__main__':
    unittest.main()

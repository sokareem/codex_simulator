import unittest
from unittest.mock import patch, MagicMock
import os

from codex_simulator.tools.safe_directory_tool import SafeDirectoryTool

class TestSafeDirectoryTool(unittest.TestCase):

    @patch('os.path.abspath')
    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.join')
    @patch('os.path.getsize')
    def test_list_directory_success(self, mock_getsize, mock_join, mock_listdir, mock_isdir_path, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeDirectoryTool()

        # Setup mocks
        mock_abspath.return_value = "/abs/current/test_dir"
        mock_expanduser.side_effect = lambda x: x # Keep path as is
        mock_exists.return_value = True
        mock_isdir_path.return_value = True # The path itself is a directory
        mock_listdir.return_value = ["file1.txt", "subdir"]

        # Mock behavior for items within the directory
        def join_side_effect(path, item):
            return f"{path}/{item}"
        mock_join.side_effect = join_side_effect

        # Mock os.path.isdir for items *inside* the listed directory
        def isdir_item_side_effect(path):
            if path.endswith("subdir"):
                return True
            return False
        
        # Need a new mock for os.path.isdir for items, can't reuse mock_isdir_path easily for different contexts
        with patch('os.path.isdir', side_effect=isdir_item_side_effect) as mock_isdir_item:
            mock_getsize.return_value = 1024 # for file1.txt

            result = tool._run(directory_path="test_dir")

            self.assertIn("Contents of directory 'test_dir':", result)
            self.assertIn("Directories:", result)
            self.assertIn("📁 subdir/", result)
            self.assertIn("Files:", result)
            self.assertIn("📄 file1.txt (1.0KB)", result)
            
            mock_abspath.assert_called_once_with("test_dir")
            mock_expanduser.assert_called_once_with("test_dir")
            mock_exists.assert_called_once_with("/abs/current/test_dir")
            # mock_isdir_path was for the main path, mock_isdir_item for contents
            # This is tricky. The _is_safe_path uses os.path.isdir, then _run uses it again.
            # Let's refine the mock_isdir_path to be specific to the _is_safe_path call.
            # For simplicity in this example, we'll assume the initial mock_isdir_path covers the first check.
            # And the new mock_isdir_item covers the internal checks.

    def test_blocked_directory(self):
        tool = SafeDirectoryTool(blocked_directories=["/etc"])
        # Mock abspath and expanduser to ensure the path matches a blocked one
        with patch('os.path.abspath', return_value="/etc/somepath"), \
             patch('os.path.expanduser', side_effect=lambda x: x):
            result = tool._run(directory_path="/etc/somepath")
            self.assertIn("Error: Access to '/etc' is restricted for security reasons", result)

    @patch('os.path.abspath', return_value="/abs/non_existent_dir")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=False)
    def test_non_existent_directory(self, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeDirectoryTool()
        result = tool._run(directory_path="non_existent_dir")
        self.assertIn("Error: Directory '/abs/non_existent_dir' does not exist", result)

    @patch('os.path.abspath', return_value="/abs/path_is_file")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=False) # Path exists but is not a directory
    def test_path_is_not_directory(self, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeDirectoryTool()
        result = tool._run(directory_path="path_is_file")
        self.assertIn("Error: Path '/abs/path_is_file' is not a directory", result)

    @patch('os.path.abspath', return_value="/abs/empty_dir")
    @patch('os.path.expanduser', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    @patch('os.listdir', return_value=[]) # Empty directory
    def test_empty_directory(self, mock_listdir, mock_isdir, mock_exists, mock_expanduser, mock_abspath):
        tool = SafeDirectoryTool()
        result = tool._run(directory_path="empty_dir")
        self.assertIn("Contents of directory 'empty_dir':", result)
        self.assertIn("Directory is empty.", result)

if __name__ == '__main__':
    unittest.main()

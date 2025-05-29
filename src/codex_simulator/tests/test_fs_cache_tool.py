import unittest
from unittest.mock import patch
import os

from codex_simulator.tools.fs_cache_tool import FSCacheTool

class TestFSCacheTool(unittest.TestCase):

    @patch('os.listdir')
    def test_caching_behavior(self, mock_listdir):
        tool = FSCacheTool()
        test_path = "/test/path"
        
        # First call: os.listdir should be called
        mock_listdir.return_value = ["file1.txt", "file2.txt"]
        result1 = tool._run(path=test_path)
        self.assertEqual(result1, ["file1.txt", "file2.txt"])
        mock_listdir.assert_called_once_with(test_path)
        
        # Second call: os.listdir should NOT be called, result from cache
        mock_listdir.reset_mock() # Reset call count for the next assertion
        result2 = tool._run(path=test_path)
        self.assertEqual(result2, ["file1.txt", "file2.txt"])
        mock_listdir.assert_not_called()

    @patch('os.listdir')
    def test_different_paths_no_cache_conflict(self, mock_listdir):
        tool = FSCacheTool()
        path1 = "/test/path1"
        path2 = "/test/path2"

        mock_listdir.side_effect = [
            ["path1_file.txt"], # For path1
            ["path2_file.txt"]  # For path2
        ]

        result_path1 = tool._run(path=path1)
        self.assertEqual(result_path1, ["path1_file.txt"])
        
        result_path2 = tool._run(path=path2)
        self.assertEqual(result_path2, ["path2_file.txt"])

        self.assertEqual(mock_listdir.call_count, 2)
        mock_listdir.assert_any_call(path1)
        mock_listdir.assert_any_call(path2)

    @patch('os.listdir', side_effect=OSError("Permission denied"))
    def test_os_listdir_error_handling(self, mock_listdir):
        tool = FSCacheTool()
        test_path = "/restricted/path"
        
        result = tool._run(path=test_path)
        self.assertEqual(len(result), 1)
        self.assertIn(f"Error reading {test_path}: Permission denied", result[0])
        mock_listdir.assert_called_once_with(test_path)
        
        # Ensure error is not cached in a way that prevents future valid reads if the tool were more complex
        # For this simple tool, the error string itself is cached.
        result_cached = tool._run(path=test_path)
        self.assertEqual(len(result_cached), 1)
        self.assertIn(f"Error reading {test_path}: Permission denied", result_cached[0])


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess

from codex_simulator.tools.safe_shell_tool import SafeShellTool

class TestSafeShellTool(unittest.TestCase):

    def test_allowed_command(self):
        tool = SafeShellTool(allowed_commands=["echo"])
        with patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "hello"
            mock_process.stderr = ""
            mock_process.returncode = 0
            mock_run.return_value = mock_process

            result = tool._run(command="echo hello")
            self.assertEqual(result, "hello")
            mock_run.assert_called_once_with("echo hello", shell=True, capture_output=True, text=True, timeout=60)

    def test_not_allowed_command(self):
        tool = SafeShellTool(allowed_commands=["ls"])
        result = tool._run(command="rm -rf /")
        self.assertIn("Error: Command 'rm' is not allowed for security reasons.", result)

    def test_blocked_command_in_tool_config(self):
        tool = SafeShellTool(allowed_commands=["git", "status"], blocked_commands=["status"])
        result = tool._run(command="git status") # base_command 'git' is allowed
        self.assertIn("Error: Command 'git' is blocked for security reasons.", result) # but 'status' is in self.blocked_commands

    def test_blocked_command_by_default_list(self):
        tool = SafeShellTool(allowed_commands=["rm"]) # Allow rm for test
        # 'rm' is in the default blocked_commands list of the class if not overridden
        # However, the constructor overrides self.blocked_commands if the argument is provided.
        # So, if we want to test default blocking, we should not provide blocked_commands in constructor.
        default_tool = SafeShellTool(allowed_commands=["rm"]) # rm is allowed
        # default_tool.blocked_commands will contain "rm"
        result_default = default_tool._run(command="rm somefile")
        self.assertIn("Error: Command 'rm' is blocked for security reasons.", result_default)


    def test_blocked_pattern(self):
        tool = SafeShellTool(allowed_commands=["echo"])
        result = tool._run(command="echo hello; rm -rf /")
        self.assertIn("Error: Command contains blocked pattern ';' for security reasons.", result)

    def test_empty_command(self):
        tool = SafeShellTool()
        result = tool._run(command="")
        self.assertEqual(result, "Error: Empty command.")

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_python_file_creation_and_execution(self, mock_file_open, mock_exists, mock_run):
        tool = SafeShellTool(allowed_commands=["python"])
        
        mock_process = MagicMock()
        mock_process.stdout = "Python script output"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        command_with_code = "python test_script.py ```python\nprint('hello from script')\n```"
        result = tool._run(command=command_with_code)

        mock_exists.assert_called_with("test_script.py")
        mock_file_open.assert_called_once_with("test_script.py", 'w')
        mock_file_open().write.assert_called_once_with("print('hello from script')")
        
        mock_run.assert_called_once_with("python test_script.py ```python\nprint('hello from script')\n```", shell=True, capture_output=True, text=True, timeout=60)
        self.assertEqual(result, "Python script output")


    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True) # File exists
    @patch('os.chmod')
    @patch('os.stat')
    def test_python_permission_denied_then_chmod(self, mock_stat, mock_chmod, mock_exists, mock_run):
        tool = SafeShellTool(allowed_commands=["python"])

        # Simulate initial permission denied, then success after chmod
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = 0o644 # Non-executable
        mock_stat.return_value = mock_stat_result

        mock_run_results = []
        # First call: permission denied
        perm_denied_process = MagicMock()
        perm_denied_process.stdout = ""
        perm_denied_process.stderr = "Permission denied"
        perm_denied_process.returncode = 1
        mock_run_results.append(perm_denied_process)

        # Second call: success
        success_process = MagicMock()
        success_process.stdout = "Script ran fine"
        success_process.stderr = ""
        success_process.returncode = 0
        mock_run_results.append(success_process)
        
        mock_run.side_effect = mock_run_results

        command = "python existing_script.py"
        result = tool._run(command=command)

        mock_exists.assert_called_with("existing_script.py")
        mock_stat.assert_called_once_with("existing_script.py")
        mock_chmod.assert_called_once_with("existing_script.py", 0o644 | 0o100)
        self.assertEqual(mock_run.call_count, 2)
        self.assertIn("Script ran fine", result)


    @patch('subprocess.run')
    def test_command_timeout(self, mock_run):
        tool = SafeShellTool(allowed_commands=["sleep"])
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 100", timeout=60)
        
        result = tool._run(command="sleep 100")
        self.assertIn("Error: Command 'sleep 100' timed out after 60 seconds.", result)

if __name__ == '__main__':
    unittest.main()

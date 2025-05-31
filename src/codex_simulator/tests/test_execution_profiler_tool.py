import unittest
from unittest.mock import patch, MagicMock
import time
import subprocess

from codex_simulator.tools.execution_profiler_tool import ExecutionProfilerTool

class TestExecutionProfilerTool(unittest.TestCase):

    @patch('time.perf_counter')
    @patch('subprocess.run')
    def test_successful_command_execution(self, mock_subprocess_run, mock_perf_counter):
        tool = ExecutionProfilerTool()

        # Mock time.perf_counter to control duration
        mock_perf_counter.side_effect = [10.0, 10.5] # start_time, end_time

        # Mock subprocess.run for a successful command
        mock_process = MagicMock()
        mock_process.stdout = "Command output"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        command_to_run = "echo success"
        result = tool._run(command=command_to_run)

        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["duration_s"], 0.5)
        self.assertEqual(result["result"], "Command output")
        mock_subprocess_run.assert_called_once_with(
            command_to_run, shell=True, capture_output=True, text=True, timeout=60
        )

    @patch('time.perf_counter')
    @patch('subprocess.run')
    def test_failed_command_execution(self, mock_subprocess_run, mock_perf_counter):
        tool = ExecutionProfilerTool()
        mock_perf_counter.side_effect = [20.0, 20.2]
        
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = "Error message"
        mock_process.returncode = 1 # Non-zero return code indicates failure
        mock_subprocess_run.return_value = mock_process

        command_to_run = "false_command"
        result = tool._run(command=command_to_run)

        self.assertEqual(result["status"], "error")
        self.assertAlmostEqual(result["duration_s"], 0.2)
        self.assertEqual(result["result"], "Error: Error message")

    @patch('time.perf_counter')
    @patch('subprocess.run')
    def test_command_timeout(self, mock_subprocess_run, mock_perf_counter):
        tool = ExecutionProfilerTool()
        mock_perf_counter.side_effect = [30.0, 95.0] # Simulates a long execution before timeout is caught
        
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 100", timeout=60)

        command_to_run = "sleep 100"
        result = tool._run(command=command_to_run)

        self.assertEqual(result["status"], "error")
        # Duration will be calculated until the exception
        self.assertAlmostEqual(result["duration_s"], 65.0) 
        self.assertIn("Command 'sleep 100' timed out after 60 seconds", result["result"])

    @patch('time.perf_counter')
    @patch('subprocess.run')
    def test_command_no_output(self, mock_subprocess_run, mock_perf_counter):
        tool = ExecutionProfilerTool()
        mock_perf_counter.side_effect = [40.0, 40.1]

        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        command_to_run = "true" # A command that typically produces no output
        result = tool._run(command=command_to_run)

        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["duration_s"], 0.1)
        self.assertEqual(result["result"], f"Command '{command_to_run}' executed successfully (no output)")


if __name__ == '__main__':
    unittest.main()

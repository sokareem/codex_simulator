import unittest
from unittest.mock import MagicMock

from codex_simulator.tools.delegate_tool import DelegateTool

class MockAgent:
    def __init__(self, name="MockAgent"):
        self.name = name
        self.role = name # For matching purposes

    def execute(self, task_description: str):
        return f"{self.name} executed: {task_description}"

    def run(self, task_description: str): # Some agents might have run
        return f"{self.name} ran: {task_description}"

class TestDelegateTool(unittest.TestCase):

    def setUp(self):
        self.mock_file_navigator = MockAgent(name="FileNavigator")
        self.mock_code_executor = MockAgent(name="CodeExecutor")
        
        self.agents_dict = {
            "FileNavigator": self.mock_file_navigator,
            "CodeExecutor": self.mock_code_executor
        }
        self.delegate_tool = DelegateTool(agents_dict=self.agents_dict)

    def test_delegate_to_existing_agent_execute(self):
        task = "List files in /tmp"
        coworker = "FileNavigator"
        context = "User requested directory listing"
        
        result = self.delegate_tool._run(task=task, coworker=coworker, context=context)
        
        expected_delegated_task = f"{task}\n\nContext: {context}"
        self.assertEqual(result, f"FileNavigator executed: {expected_delegated_task}")

    def test_delegate_to_existing_agent_run(self):
        # Mock an agent that only has a 'run' method
        mock_runner_agent = MockAgent(name="RunnerAgent")
        delattr(mock_runner_agent, 'execute') # Remove execute method
        
        temp_agents_dict = {"RunnerAgent": mock_runner_agent}
        tool_with_runner = DelegateTool(agents_dict=temp_agents_dict)

        task = "Run this script"
        coworker = "RunnerAgent"
        result = tool_with_runner._run(task=task, coworker=coworker)
        self.assertEqual(result, f"RunnerAgent ran: {task}")


    def test_delegate_to_non_existent_agent(self):
        task = "Do something impossible"
        coworker = "NonExistentAgent"
        
        result = self.delegate_tool._run(task=task, coworker=coworker)
        self.assertIn("Error: Could not find agent 'NonExistentAgent' for delegation.", result)
        self.assertIn("Available agents: FileNavigator, CodeExecutor", result)

    def test_delegate_with_complex_dict_input_for_task(self):
        # Test the _extract_str_from_dict logic
        task_dict = {"description": "My complex task", "priority": "high"}
        coworker = "CodeExecutor"
        
        result = self.delegate_tool._run(task=task_dict, coworker=coworker) # type: ignore
        expected_delegated_task = "My complex task" # Extracted from dict
        self.assertEqual(result, f"CodeExecutor executed: {expected_delegated_task}")

    def test_delegate_with_case_insensitive_coworker_name(self):
        task = "Execute command"
        coworker = "codeexecutor" # Lowercase
        
        result = self.delegate_tool._run(task=task, coworker=coworker)
        self.assertEqual(result, f"CodeExecutor executed: {task}")

    def test_delegate_coworker_name_partial_match(self):
        task = "Navigate to /home"
        coworker = "Navigator" # Partial match for FileNavigator
        
        result = self.delegate_tool._run(task=task, coworker=coworker)
        self.assertEqual(result, f"FileNavigator executed: {task}")

    def test_agent_has_no_executable_method(self):
        no_method_agent = MagicMock(spec=[]) # Agent with no execute or run
        no_method_agent.role = "NoMethodAgent"

        temp_agents_dict = {"NoMethodAgent": no_method_agent}
        tool_with_no_method_agent = DelegateTool(agents_dict=temp_agents_dict)
        
        result = tool_with_no_method_agent._run(task="test", coworker="NoMethodAgent")
        self.assertIn("Error: Agent has no executable method.", result)


if __name__ == '__main__':
    unittest.main()

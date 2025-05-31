import unittest
from codex_simulator.tools.custom_tool import MyCustomTool, MyCustomToolInput

class TestMyCustomTool(unittest.TestCase):

    def test_run_my_custom_tool(self):
        tool = MyCustomTool()
        test_argument = "test_input"
        
        # The tool's _run method takes 'argument' as a keyword argument
        result = tool._run(argument=test_argument)
        
        # According to the tool's implementation:
        # return "this is an example of a tool output, ignore it and move along."
        self.assertEqual(result, "this is an example of a tool output, ignore it and move along.")

    def test_args_schema(self):
        # This test just checks if the args_schema is correctly defined
        # and can be instantiated, which Pydantic handles.
        try:
            MyCustomToolInput(argument="some_arg")
            schema_valid = True
        except Exception:
            schema_valid = False
        self.assertTrue(schema_valid, "MyCustomToolInput schema should be valid.")

if __name__ == '__main__':
    unittest.main()

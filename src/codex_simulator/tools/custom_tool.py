from typing import Type
from pydantic import BaseModel, Field

# Only import crewai if available, otherwise create stub
try:
    from crewai.tools import BaseTool
except ImportError:
    # Create a stub BaseTool for testing
    class BaseTool:
        name: str = "stub_tool"
        description: str = "Stub tool for testing"
        
        def _run(self, **kwargs):
            return "Stub tool output"
        
        def run(self, **kwargs):
            return self._run(**kwargs)

class MyCustomToolInput(BaseModel):
    """Input for the custom tool."""
    argument: str = Field(..., description="An argument for the custom tool")

class MyCustomTool(BaseTool):
    """A custom tool for demonstration purposes."""
    name: str = "my_custom_tool"
    description: str = "A custom tool for demonstration"
    args_schema: Type[BaseModel] = MyCustomToolInput
    
    def _run(self, argument: str):
        """Run the custom tool."""
        return "this is an example of a tool output, ignore it and move along."

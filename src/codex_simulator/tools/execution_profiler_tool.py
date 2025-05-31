import time
import subprocess
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class ExecutionProfilerToolInput(BaseModel):
    """Input for ExecutionProfilerTool."""
    command: str = Field(..., description="The shell command to profile for execution time")

class ExecutionProfilerTool(BaseTool):
    """Measure execution time and success/failure of commands."""
    name: str = "execution_profiler_tool"
    description: str = "Profiles execution time and outcomes of shell commands."
    args_schema: Type[BaseModel] = ExecutionProfilerToolInput
    
    # Include model_config to allow arbitrary types
    model_config = {"arbitrary_types_allowed": True}

    def _run(self, command: str) -> dict:
        """Execute a command and measure its performance."""
        start = time.perf_counter()
        
        try:
            # Run the command using subprocess
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            # Format the output
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output:
                    output += "\n\n"
                output += "Error: " + result.stderr
            
            if not output:
                output = f"Command '{command}' executed successfully (no output)"
                
            status = "success" if result.returncode == 0 else "error"
            
        except Exception as e:
            output = str(e)
            status = "error"
            
        elapsed = time.perf_counter() - start
        
        return {
            "status": status,
            "duration_s": round(elapsed, 4),
            "result": output
        }

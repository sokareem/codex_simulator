"""
Tool adapter for Claude Code-style interface.
Maps existing CodexSimulator tools to Claude Code tool names and functionalities.
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from pathlib import Path

# Import your existing tools
from .safe_shell_tool import SafeShellTool
from .safe_file_read_tool import SafeFileReadTool
from .safe_file_write_tool import SafeFileWriteTool
from .safe_directory_tool import SafeDirectoryTool

# Optional web tools
try:
    from .serp_api_tool import SerpAPITool
    from .website_tool import WebsiteTool
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    SerpAPITool = None
    WebsiteTool = None
    WEB_TOOLS_AVAILABLE = False


class ClaudeToolAdapter:
    """Adapts existing CodexSimulator tools to a Claude Code-style interface."""

    def __init__(self, use_mcp: bool = False, mcp_server_url: Optional[str] = None):
        self.use_mcp = use_mcp
        self.mcp_server_url = mcp_server_url

        # Initialize your existing tools
        self.safe_shell = SafeShellTool()
        self.safe_read = SafeFileReadTool()
        self.safe_write = SafeFileWriteTool()
        self.safe_dir = SafeDirectoryTool()
        
        if WEB_TOOLS_AVAILABLE:
            try:
                self.serp_api = SerpAPITool()
                self.website_tool = WebsiteTool()
            except Exception:
                self.serp_api = None
                self.website_tool = None
                print("⚠️ Web research tools (SerpAPITool, WebsiteTool) initialization failed.")
        else:
            self.serp_api = None
            self.website_tool = None

        # Map Claude tool names to methods in this adapter
        self.tool_map: Dict[str, Callable[..., Awaitable[Any]]] = {
            "Bash": self._execute_bash,
            "Read": self._read_file,
            "Write": self._write_file,
            "Edit": self._edit_file,
            "LS": self._list_directory,
            "Grep": self._grep_files,
            "Glob": self._glob_files,
            "WebSearch": self._web_search,
            "WebFetch": self._web_fetch,
        }

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by its Claude Code name."""
        if tool_name not in self.tool_map:
            return f"Error: Tool '{tool_name}' not recognized."

        try:
            return await self.tool_map[tool_name](**args)
        except TypeError as e:
            return f"Error: Invalid arguments for tool '{tool_name}'. Details: {e}. Args provided: {args}"
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

    async def _execute_bash(self, command: str, timeout: int = 60) -> str:
        """Adapts SafeShellTool for Bash commands."""
        try:
            return self.safe_shell.run(commands=[command], timeout=timeout)
        except Exception as e:
            return f"Bash execution error: {e}"

    async def _read_file(self, path: str) -> str:
        """Adapts SafeFileReadTool."""
        try:
            return self.safe_read.run(file_path=path)
        except Exception as e:
            return f"File read error for {path}: {e}"

    async def _write_file(self, path: str, content: str) -> str:
        """Adapts SafeFileWriteTool."""
        try:
            return self.safe_write.run(file_path=path, text=content)
        except Exception as e:
            return f"File write error for {path}: {e}"

    async def _edit_file(self, path: str, changes: list) -> str:
        """
        Adapts SafeFileWriteTool for edits. This is a simplified implementation.
        """
        if len(changes) == 1 and changes[0].get('type') == 'replace_content' and 'content' in changes[0]:
            return await self._write_file(path, changes[0]['content'])
        
        return f"Error: 'Edit' tool with complex changes not fully implemented. Path: {path}. For full rewrite, use 'Write'."

    async def _list_directory(self, path: str = ".", recursive: bool = False, depth: int = 1) -> str:
        """Adapts SafeDirectoryTool for LS."""
        try:
            return self.safe_dir.run(directory_path=path, recursive=recursive, depth=depth if recursive else 1)
        except Exception as e:
            return f"Directory listing error for {path}: {e}"

    async def _grep_files(self, pattern: str, path: str = ".", is_recursive: bool = True, is_case_sensitive: bool = False) -> str:
        """Implements Grep functionality using Python-based search."""
        results = []
        base_path = Path(path).resolve()
        files_to_search = []

        if base_path.is_file():
            files_to_search.append(base_path)
        elif base_path.is_dir():
            if is_recursive:
                files_to_search.extend(base_path.rglob("*"))
            else:
                files_to_search.extend(base_path.glob("*"))
        else:
            return f"Error: Path '{path}' is not a valid file or directory."

        for file_path_obj in files_to_search:
            if file_path_obj.is_file():
                try:
                    content = file_path_obj.read_text(encoding='utf-8', errors='ignore')
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        match_line = line if is_case_sensitive else line.lower()
                        match_pattern = pattern if is_case_sensitive else pattern.lower()
                        if match_pattern in match_line:
                            try:
                                relative_path = file_path_obj.relative_to(Path.cwd())
                            except ValueError:
                                relative_path = file_path_obj
                            results.append(f"{relative_path}:{i+1}:{line.strip()}")
                except Exception:
                    pass 
        
        if not results:
            return f"No matches found for '{pattern}' in '{path}'."
        return "\n".join(results)

    async def _glob_files(self, pattern: str, path: str = ".") -> str:
        """Implements Glob functionality using pathlib."""
        try:
            base_path = Path(path).resolve()
            if not base_path.is_dir():
                return f"Error: Path '{path}' is not a directory for glob operation."

            matches = []
            for p in base_path.glob(pattern):
                try:
                    relative_path = p.relative_to(Path.cwd())
                except ValueError:
                    relative_path = p
                matches.append(str(relative_path))
            
            if not matches:
                return f"No files found matching glob pattern '{pattern}' in '{path}'."
            return "\n".join(matches)
        except Exception as e:
            return f"Glob error for pattern '{pattern}' in '{path}': {e}"

    async def _web_search(self, query: str, num_results: int = 5) -> str:
        """Adapts SerpAPITool for web searches."""
        if not self.serp_api:
            return "Error: Web search tool (SerpAPITool) is not available or configured."
        try:
            return self.serp_api.run(query=query)
        except Exception as e:
            return f"Web search error for query '{query}': {e}"

    async def _web_fetch(self, url: str) -> str:
        """Adapts WebsiteTool for fetching web content."""
        if not self.website_tool:
            return "Error: Web fetch tool (WebsiteTool) is not available or configured."
        try:
            return self.website_tool.run(website_url=url)
        except Exception as e:
            return f"Web fetch error for URL '{url}': {e}"

    def get_available_tools(self) -> Dict[str, str]:
        """Returns a dictionary of available tools and their descriptions."""
        tool_descriptions = {
            "Bash": "Executes shell commands in your environment.",
            "Read": "Reads the contents of files.",
            "Write": "Creates or overwrites files.",
            "Edit": "Makes targeted edits to specific files. (Simplified: full rewrite)",
            "LS": "Lists files and directories.",
            "Grep": "Searches for patterns in file contents. (Python-based)",
            "Glob": "Finds files based on pattern matching.",
        }
        if self.serp_api:
            tool_descriptions["WebSearch"] = "Performs web searches."
        if self.website_tool:
            tool_descriptions["WebFetch"] = "Fetches content from a specified URL."
        
        available = {name: desc for name, desc in tool_descriptions.items() if name in self.tool_map}
        return available

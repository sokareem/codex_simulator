from typing import List
import os
from crewai.tools import BaseTool

class FSCacheTool(BaseTool):
    """Cache and return directory listings to avoid repeated disk I/O."""
    name: str = "fs_cache_tool"
    description: str = "Caches directory listings to avoid repeated filesystem access operations."

    def __init__(self):
        super().__init__()
        self._cache = {}

    def _run(self, path: str) -> List[str]:
        # Return cached listing if available
        if path in self._cache:
            return self._cache[path]
        # Otherwise read and cache
        try:
            files = os.listdir(path)
            self._cache[path] = files
            return files
        except Exception as e:
            return [f"Error reading {path}: {e}"]

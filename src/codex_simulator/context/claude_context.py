"""
Context management for Claude Code-style interface.
Handles loading and providing context from CLAUDE.md files.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class ClaudeContextManager:
    """
    Manages context from CLAUDE.md files (project, user, local).
    Follows Claude Code's memory lookup and import logic.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        
        # Define memory file locations
        self.project_memory_file = self.project_root / "CLAUDE.md"
        self.user_memory_file = Path.home() / ".claude" / "CLAUDE.md"
        self.project_local_memory_file = self.project_root / "CLAUDE.local.md"

        # Loaded memory content
        self.project_memory_content: str = ""
        self.user_memory_content: str = ""
        self.project_local_memory_content: str = ""
        self.imported_files_content: Dict[Path, str] = {}

    def _read_file_with_imports(self, file_path: Path, visited_paths: Optional[Set[Path]] = None, depth: int = 0) -> str:
        """Reads a CLAUDE.md file and processes @-imports recursively."""
        if visited_paths is None:
            visited_paths = set()

        if file_path in visited_paths or depth > 5:
            return f"[Import skipped: cyclic or too deep - {file_path}]"

        if not file_path.exists() or not file_path.is_file():
            return ""

        visited_paths.add(file_path)
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            final_lines = []
            in_code_block = False
            for line in content.splitlines():
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    final_lines.append(line)
                    continue

                if in_code_block:
                    final_lines.append(line)
                    continue

                # Process imports in this line if not in code block
                current_line_processed = line
                for match in re.finditer(r"(?<!`)@([^\s`]+)", line):
                    import_path_str = match.group(1)
                    
                    # Resolve path: handle ~ and relative paths
                    if import_path_str.startswith("~"):
                        import_path = Path(import_path_str).expanduser()
                    else:
                        import_path = (file_path.parent / import_path_str).resolve()
                    
                    # Read imported file
                    if import_path not in self.imported_files_content:
                        if import_path in visited_paths:
                            imported_content = f"[Import skipped: cyclic - {import_path}]"
                        else:
                            new_visited = visited_paths.copy()
                            imported_content = self._read_file_with_imports(import_path, new_visited, depth + 1)
                        self.imported_files_content[import_path] = imported_content
                    else:
                        imported_content = self.imported_files_content[import_path]
                    
                    # Replace in line
                    current_line_processed = current_line_processed.replace(
                        match.group(0), 
                        f"\n--- Imported Content: {import_path_str} ---\n{imported_content}\n--- End Imported Content: {import_path_str} ---\n", 
                        1
                    )
                final_lines.append(current_line_processed)
            
            return "\n".join(final_lines)

        except Exception as e:
            return f"[Error reading/processing {file_path}: {e}]"

    def load_project_memory(self, reload: bool = False):
        """Loads project-specific CLAUDE.md from current or specified project root."""
        if reload:
            self.project_root = Path.cwd()
            self.project_memory_file = self.project_root / "CLAUDE.md"
            self.project_local_memory_file = self.project_root / "CLAUDE.local.md"
            self.imported_files_content.clear()

        self.project_memory_content = self._read_file_with_imports(self.project_memory_file)
        if self.project_memory_content:
            print(f"📋 Loaded project memory from {self.project_memory_file}")

    def load_user_memory(self):
        """Loads user-specific CLAUDE.md from ~/.claude/CLAUDE.md."""
        self._ensure_user_memory_exists()
        self.user_memory_content = self._read_file_with_imports(self.user_memory_file)
        if self.user_memory_content:
             print(f"📋 Loaded user memory from {self.user_memory_file}")

    def load_project_local_memory(self):
        """Loads project-local CLAUDE.local.md (deprecated by Claude Code but supported for reading)."""
        self.project_local_memory_content = self._read_file_with_imports(self.project_local_memory_file)
        if self.project_local_memory_content:
            print(f"📋 Loaded project-local memory from {self.project_local_memory_file} (Note: CLAUDE.local.md is deprecated by Claude Code)")

    def _ensure_project_memory_exists(self):
        """Ensures ./CLAUDE.md exists, creating a default one if not."""
        if not self.project_memory_file.exists():
            default_content = f"# Claude Project Memory: {self.project_root.name}\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## Project-Specific Notes\n- (Add your project notes, coding standards, common commands here)\n"
            try:
                self.project_memory_file.write_text(default_content, encoding='utf-8')
                print(f"✅ Created default project CLAUDE.md at {self.project_memory_file}")
            except Exception as e:
                print(f"⚠️ Could not create default project CLAUDE.md: {e}")
    
    def _ensure_user_memory_exists(self):
        """Ensures ~/.claude/CLAUDE.md exists, creating a default one if not."""
        user_claude_dir = Path.home() / ".claude"
        try:
            user_claude_dir.mkdir(parents=True, exist_ok=True)
            if not self.user_memory_file.exists():
                default_content = f"# Claude User Memory\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## Personal Preferences & Notes\n- (Add your global preferences, common snippets, tool aliases here)\n"
                self.user_memory_file.write_text(default_content, encoding='utf-8')
                print(f"✅ Created default user CLAUDE.md at {self.user_memory_file}")
        except Exception as e:
            print(f"⚠️ Could not create user CLAUDE.md directory or file: {e}")

    def get_full_context(self) -> str:
        """Combines all loaded memory contexts."""
        contexts = []
        
        # User memory
        if self.user_memory_content:
            contexts.append(f"--- User Memory ({self.user_memory_file}) ---\n{self.user_memory_content}")

        # Current project's CLAUDE.md
        if self.project_memory_content:
            contexts.append(f"--- Project Memory ({self.project_memory_file}) ---\n{self.project_memory_content}")

        # Current project's CLAUDE.local.md (if exists and loaded)
        if self.project_local_memory_content:
            contexts.append(f"--- Project Local Memory ({self.project_local_memory_file}) ---\n{self.project_local_memory_content}")
            
        return "\n\n".join(contexts).strip()

    def add_to_memory(self, text: str, location: str = "project"):
        """Adds text to the specified memory file."""
        target_file = None
        if location == "project":
            target_file = self.project_memory_file
            self._ensure_project_memory_exists()
        elif location == "user":
            target_file = self.user_memory_file
            self._ensure_user_memory_exists()
        else:
            print(f"❌ Unknown memory location: {location}")
            return

        if target_file:
            try:
                with target_file.open("a", encoding="utf-8") as f:
                    f.write(f"\n\n# Added on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{text}\n")
                print(f"💾 Added to {location} memory ({target_file}).")
                # Reload the specific memory
                if location == "project": 
                    self.load_project_memory(reload=True)
                if location == "user": 
                    self.load_user_memory()
            except Exception as e:
                print(f"❌ Failed to write to {location} memory: {e}")

    def add_to_project_memory(self, text: str):
        self.add_to_memory(text, "project")

    def add_to_user_memory(self, text: str):
        self.add_to_memory(text, "user")

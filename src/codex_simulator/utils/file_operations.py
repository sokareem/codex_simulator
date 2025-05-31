"""
File operations manager for handling read/write operations with proper permissions.
"""
import os
import sys
from typing import Optional, List, Dict, Any, Tuple

class FileOperationsManager:
    """Manages file operations with permission controls."""
    
    @staticmethod
    def read_file(file_path: str, max_size: int = 5 * 1024 * 1024) -> Tuple[bool, str]:
        """
        Read a file with basic safety checks.
        
        Args:
            file_path: Path to the file
            max_size: Maximum file size to read
            
        Returns:
            Tuple containing success status and content/error message
        """
        try:
            file_path = os.path.abspath(os.path.expanduser(file_path))
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False, f"File '{file_path}' does not exist."
                
            # Check if it's a file
            if not os.path.isfile(file_path):
                return False, f"Path '{file_path}' is not a file."
                
            # Check file size
            if os.path.getsize(file_path) > max_size:
                return False, f"File '{file_path}' exceeds the maximum allowed size of {max_size/1024/1024:.1f}MB"
            
            # Check for binary content
            is_binary = False
            try:
                with open(file_path, 'rb') as f:
                    initial_bytes = f.read(1024)
                    is_binary = b'\x00' in initial_bytes
                    if is_binary:
                        return False, f"File '{file_path}' appears to be binary. Cannot display content."
            except:
                pass
                
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            return True, content
            
        except PermissionError:
            return False, f"Permission denied to access file '{file_path}'."
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(file_path: str, content: str, append: bool = False) -> Tuple[bool, str]:
        """
        Write to a file after requesting user permission.
        
        Args:
            file_path: Path to the file
            content: Content to write
            append: Whether to append or overwrite
            
        Returns:
            Tuple containing success status and result/error message
        """
        try:
            file_path = os.path.abspath(os.path.expanduser(file_path))
            operation = "append to" if append else "write to"
            
            # Request permission
            print("\n" + "="*80)
            print(f"⚠️  PERMISSION REQUIRED: {operation.upper()} FILE")
            print("="*80)
            print(f"File: {file_path}")
            print("-"*80)
            print("Preview of content to be written:")
            print("-"*80)
            
            # Show preview with line numbers (limit to 20 lines if content is long)
            lines = content.split('\n')
            if len(lines) > 20:
                print('\n'.join(f"{i+1:3d} | {line}" for i, line in enumerate(lines[:20])))
                print(f"... (and {len(lines)-20} more lines)")
            else:
                print('\n'.join(f"{i+1:3d} | {line}" for i, line in enumerate(lines)))
            
            print("-"*80)
            response = input("Allow this operation? (y/n): ").strip().lower()
            
            if response not in ['y', 'yes']:
                return False, f"Operation cancelled: {operation} {file_path}"
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # Write the file
            mode = "a" if append else "w"
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
                
            return True, f"Successfully {operation} {file_path}"
            
        except Exception as e:
            return False, f"Error writing to file: {str(e)}"

"""
Permission manager to handle user confirmations for potentially risky operations.
"""
import os
from typing import Optional, Callable, Any

class PermissionManager:
    """Manages permissions for potentially risky operations."""
    
    @staticmethod
    def request_file_write_permission(file_path: str, content: str, operation: str = "write to") -> bool:
        """
        Request user permission to write to a file.
        
        Args:
            file_path: Path to the file
            content: Content to be written
            operation: Type of operation (write/append)
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        print("\n" + "="*80)
        print(f"⚠️  PERMISSION REQUIRED: {operation.upper()} FILE")
        print("="*80)
        print(f"File: {os.path.abspath(file_path)}")
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
        return response in ['y', 'yes']

    @staticmethod
    def with_permission(operation_name: str, 
                        check_func: Callable[[Any], bool] = None) -> Callable:
        """
        Decorator for operations that require permission.
        
        Args:
            operation_name: Name of the operation requiring permission
            check_func: Optional function to determine if permission is actually needed
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Check if we should ask for permission
                if check_func and not check_func(*args, **kwargs):
                    return func(*args, **kwargs)
                
                print(f"\n⚠️  Permission required for: {operation_name}")
                response = input("Allow this operation? (y/n): ").strip().lower()
                
                if response in ['y', 'yes']:
                    return func(*args, **kwargs)
                else:
                    return f"Operation cancelled: {operation_name}"
            return wrapper
        return decorator

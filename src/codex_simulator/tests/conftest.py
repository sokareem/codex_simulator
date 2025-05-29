"""
Configure test environment for all test modules.
This file is automatically loaded by pytest before any tests run.
"""
import os
import sys
import pytest

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Add src directory to path as well
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment by ensuring paths are properly configured."""
    try:
        import codex_simulator
        print(f"Successfully imported codex_simulator from: {codex_simulator.__file__}")
        
        # Try to import key dependencies to verify they're available
        import pydantic
        print(f"Successfully imported pydantic {pydantic.__version__}")
        
        import requests
        print(f"Successfully imported requests {requests.__version__}")
        
        import dotenv
        print(f"Successfully imported python-dotenv {dotenv.__version__}")
        
    except ImportError as e:
        print(f"Warning: Import error during test setup: {e}")
        print(f"Current sys.path: {sys.path}")
        
    return None

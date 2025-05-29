import os
import sys
import unittest

def run_tests():
    """Discovers and runs all tests in the current directory and subdirectories."""
    # Add the project root to sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Add src directory to path as well
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Print the current Python path to help debug
    print("Python path:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Check if the test directory exists
    test_dir = os.path.dirname(__file__)
    print(f"Test directory: {test_dir}")
    if not os.path.isdir(test_dir):
        print(f"ERROR: Test directory not found: {test_dir}")
        sys.exit(1)
        
    # Try to import the module to verify it's in the path
    try:
        import codex_simulator
        print(f"Successfully imported codex_simulator module from: {codex_simulator.__file__}")
    except ImportError as e:
        print(f"Failed to import codex_simulator: {e}")
        print("Attempting to continue anyway...")
    
    # Load and run tests
    print(f"Looking for tests in: {test_dir}")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern='test_*.py')
    
    if not list(suite):
        print(f"WARNING: No tests found in {test_dir}")
        # Try to list .py files in the directory to diagnose
        try:
            py_files = [f for f in os.listdir(test_dir) if f.endswith('.py')]
            print(f"Python files in directory: {py_files}")
        except Exception as e:
            print(f"Could not list directory contents: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with a non-zero status if tests failed
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    run_tests()

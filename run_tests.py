#!/usr/bin/env python
"""
Simple test runner that makes sure the correct test directory is used.
"""
import os
import sys

# Ensure we're using the correct path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the actual test runner
from src.codex_simulator.tests.run_all_tests import run_tests

if __name__ == "__main__":
    print(f"Running tests from: {project_root}")
    run_tests()

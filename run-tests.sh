#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to clean up the temporary directory on exit
cleanup() {
    echo "Cleaning up temporary directory..."
    if [ -d "$PROJECT_TMP_DIR" ]; then
        rm -rf "$PROJECT_TMP_DIR"
        echo "Removed $PROJECT_TMP_DIR"
    fi
}

# Register the cleanup function to be called on EXIT signal
trap cleanup EXIT

# Define a project-specific temporary directory
# Assuming the script is run from the project root or cd's to it.
# Let's ensure we are in the project root first.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR" # Ensure we are in the project root

PROJECT_TMP_DIR="${SCRIPT_DIR}/.tmp_pip_tests"
mkdir -p "$PROJECT_TMP_DIR"
export TMPDIR="$PROJECT_TMP_DIR"
echo "TMPDIR set to: $TMPDIR"
echo "--------------------------------------------------"

# Bootstrap pip if missing
echo "Ensuring pip is installed..."
if python -m pip --version &> /dev/null; then
    echo "pip is already available. Skipping ensurepip."
else
    echo "pip not found or not functional. Attempting to bootstrap with ensurepip..."
    if ! python -m ensurepip --upgrade; then
        echo "ERROR: 'python -m ensurepip --upgrade' failed."
        echo "This might indicate an issue with your Python installation."
        echo "Please ensure your Python environment is correctly set up and not corrupted."
        exit 1
    fi
    echo "ensurepip completed."
fi

python -m pip install --upgrade pip

# Script to install test dependencies and run tests

echo "Ensuring the correct Python environment is used for testing..."
echo "--------------------------------------------------"
echo "Current PATH: $PATH"
echo "--------------------------------------------------"
echo "Which Python: $(which python)"
echo "Python version:"
python --version
echo "--------------------------------------------------"
echo "Which pip: $(which pip)"
echo "Pip version:"
python -m pip --version
echo "--------------------------------------------------"

# Install pydantic first (most critical dependency)
echo "Installing pydantic first using 'python -m pip'..."
python -m pip install pydantic>=2.4.2

# Install test dependencies from requirements-test.txt
echo "Installing test dependencies from requirements-test.txt using 'python -m pip'..."
python -m pip install -r requirements-test.txt

# Install the package in development mode with test dependencies
echo "Installing codex_simulator package in development mode using 'python -m pip'..."
python -m pip install -e ".[test]"
echo "--------------------------------------------------"

echo "Listing installed packages in the current environment:"
python -m pip list
echo "--------------------------------------------------"

# Run the tests
echo "Running tests from the correct directory..."
# Set PYTHONPATH to include the project src directory and the project root
# Prepending src allows `import codex_simulator`
# Prepending project_root allows `import src.codex_simulator` if CWD changes
export PYTHONPATH="${SCRIPT_DIR}/src:${SCRIPT_DIR}:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"
echo "--------------------------------------------------"

# Run from the project root to avoid path confusion
# cd /Users/sinmi/Projects/codex_simulator # Already cd'd via SCRIPT_DIR
echo "Current working directory: $(pwd)"
echo "Executing tests with: python -m src.codex_simulator.tests.run_all_tests"
python -m src.codex_simulator.tests.run_all_tests

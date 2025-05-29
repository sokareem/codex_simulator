#!/bin/bash

# Navigate to the project directory 
cd "$(dirname "$0")"

# Install the package in development mode
pip install -e .

echo "codex_simulator has been installed globally."
echo "You can now run it from any directory using:"
echo "  • codex_simulator"
echo "  • run_crew"
echo "  • train"
echo "  • replay"
echo "  • test"

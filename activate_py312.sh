#!/bin/bash
# Activation script for Python 3.12 CodexSimulator environment

PROJECT_ROOT="/Users/sinmi/Projects/codex_simulator"
VENV_PATH="$PROJECT_ROOT/.venv312"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Python 3.12 virtual environment not found!"
    echo "Run: python setup_python312_env.py"
    exit 1
fi

echo "🚀 Activating Python 3.12 CodexSimulator environment..."
source "$VENV_PATH/bin/activate"

echo "✅ Environment activated!"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo ""
echo "Available commands:"
echo "  • python run_direct.py"
echo "  • python -m codex_simulator"
echo "  • python src/codex_simulator/main.py"
echo ""
echo "To deactivate: deactivate"

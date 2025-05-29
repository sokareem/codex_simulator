#!/bin/bash
# Complete setup and run script for CodexSimulator with Python 3.12

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 CodexSimulator Setup and Run Script"
echo "======================================"

# Check if Python 3.12 environment exists
if [ ! -d ".venv312" ]; then
    echo "📦 Setting up Python 3.12 environment..."
    python3 setup_python312_env.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to setup Python 3.12 environment"
        exit 1
    fi
fi

echo "🔄 Activating Python 3.12 environment..."
source .venv312/bin/activate

echo "✅ Environment activated!"
echo "Python version: $(python --version)"

echo "🚀 Starting CodexSimulator..."
python run_direct_py312.py

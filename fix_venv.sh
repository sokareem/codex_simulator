#!/bin/bash

echo "🔍 Diagnosing virtual environment issues..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "❌ No virtual environment detected"
    echo "🔧 Creating and activating virtual environment..."
    
    # Remove existing .venv if it exists
    if [ -d ".venv" ]; then
        echo "Removing existing .venv directory..."
        rm -rf .venv
    fi
    
    # Create new virtual environment
    python3 -m venv .venv
    echo "Virtual environment created at .venv"
    echo "Please run: source .venv/bin/activate"
    echo "Then run this script again."
    exit 1
fi

echo "🐍 Python executable: $(which python)"
echo "📦 Pip executable: $(which pip)"

# Upgrade pip first
echo "🔧 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies directly in the virtual environment
echo "📦 Installing pydantic..."
python -m pip install "pydantic>=2.4.2"

echo "📦 Installing other dependencies..."
python -m pip install -r requirements.txt

echo "🔍 Verifying installation..."
python debug_env.py

echo "🎉 Setup complete! Try running: python run_direct.py"

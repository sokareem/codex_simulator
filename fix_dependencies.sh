#!/bin/bash

echo "🔧 Fixing CodexSimulator dependencies and configuration..."

# Ensure virtual environment is activated
if [[ "$VIRTUAL_ENV" != *".venv312"* ]]; then
    echo "📦 Activating virtual environment..."
    source .venv312/bin/activate
fi

# Upgrade pip and setuptools
echo "⬆️ Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install core dependencies first
echo "📚 Installing core dependencies..."
pip install pydantic>=2.4.2
pip install "crewai[tools]>=0.86.0,<1.0.0"
pip install langchain-google-genai>=0.0.1
pip install google-generativeai>=0.3.0
pip install python-dotenv>=1.0.0

# Install essential system dependencies
echo "🔧 Installing system dependencies..."
pip install psutil>=5.9.0
pip install pyyaml>=6.0.0
pip install flask>=2.3.0

# Install additional requirements
echo "📄 Installing additional requirements..."
pip install -r requirements.txt

# Verify critical imports
echo "🔍 Verifying installations..."
python -c "
import sys
import os
sys.path.insert(0, 'src')

# Test core imports
try:
    import crewai
    print('✅ CrewAI imported successfully')
except ImportError as e:
    print(f'❌ CrewAI import failed: {e}')

try:
    import pydantic
    print('✅ Pydantic imported successfully')
except ImportError as e:
    print(f'❌ Pydantic import failed: {e}')

try:
    import yaml
    print('✅ YAML imported successfully')
except ImportError as e:
    print(f'❌ YAML import failed: {e}')

try:
    import psutil
    print('✅ psutil imported successfully')
except ImportError as e:
    print(f'❌ psutil import failed: {e}')

try:
    import flask
    print('✅ Flask imported successfully')
except ImportError as e:
    print(f'❌ Flask import failed: {e}')

# Test project imports
try:
    from codex_simulator.crew import CodexSimulator
    print('✅ CodexSimulator imported successfully')
except ImportError as e:
    print(f'❌ CodexSimulator import failed: {e}')
"

echo "🎉 Dependency fix complete!"
echo "Try running start_with_mcp.sh again"

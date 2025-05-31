#!/bin/bash
set -e

echo "🚀 Quick CodexSimulator Installation"
echo "=================================="

# Activate virtual environment if it exists
if [ -d ".venv312" ]; then
    echo "📦 Activating Python 3.12 virtual environment..."
    source .venv312/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Consider creating one:"
    echo "   python3.12 -m venv .venv312"
    echo "   source .venv312/bin/activate"
fi

echo "🔧 Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "📋 Installing with constraints to avoid conflicts..."

# Create a constraints file to help pip resolve dependencies
cat > constraints.txt << 'EOF'
protobuf>=5.26.1,<5.28.0
jsonschema==4.22.0
jinja2==3.1.2
packaging==23.2
google-ai-generativelanguage==0.4.0
google-api-core>=2.15.0,<2.20.0
langchain-core==0.1.52
EOF

echo "🎯 Installing with constraints..."
python -m pip install -c constraints.txt \
    "pydantic>=2.4.2,<2.10.0" \
    "google-generativeai==0.3.2" \
    "langchain-google-genai==0.0.9" \
    "python-dotenv>=1.0.0" \
    "requests>=2.28.0" \
    "beautifulsoup4>=4.12.0"

echo "🤖 Installing CrewAI..."
python -m pip install -c constraints.txt "crewai[tools]>=0.86.0,<0.90.0"

echo "📦 Installing additional utilities..."
python -m pip install \
    "pypdf>=4.0.0" \
    "matplotlib>=3.5.0" \
    "psutil>=5.9.0" \
    "GitPython>=3.1.0" \
    "bandit>=1.7.0"

echo "🏗️  Installing CodexSimulator in development mode..."
python -m pip install -e .

echo "🧹 Cleaning up..."
rm -f constraints.txt

echo ""
echo "🎉 Installation complete!"
echo "🚀 Try running: python run_claude_repl.py"

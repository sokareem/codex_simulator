#!/bin/bash
# Install requirements including psutil and Flask

echo "🔧 Installing all requirements for CodexSimulator..."

# Activate virtual environment
source .venv312/bin/activate

# Install/upgrade pip
pip install --upgrade pip

# Install psutil specifically first
echo "📦 Installing psutil..."
pip install "psutil>=5.9.0"

# Install Flask and web dependencies
echo "🌐 Installing web dependencies..."
pip install "flask>=2.3.0" "jinja2>=3.1.0"

# Install PDF processing
echo "📄 Installing PDF processing..."
pip install "PyPDF2>=3.0.0" "pdfplumber>=0.9.0"

# Install YAML processing
echo "📝 Installing YAML processing..."
pip install "pyyaml>=6.0.0"

# Install other requirements
echo "📚 Installing other requirements..."
pip install -r requirements.txt

echo "✅ All requirements installed successfully!"

# Verify critical imports
echo "🔍 Verifying installations..."
python -c "
import sys
sys.path.insert(0, 'src')

try:
    import psutil
    print('✅ psutil imported successfully')
except ImportError as e:
    print(f'❌ psutil import failed: {e}')

try:
    import flask
    print('✅ flask imported successfully')
except ImportError as e:
    print(f'❌ flask import failed: {e}')

try:
    import yaml
    print('✅ yaml imported successfully')
except ImportError as e:
    print(f'❌ yaml import failed: {e}')
"

echo "🎉 Installation complete!"

#!/bin/bash

echo "🔧 Installing psutil for CodexSimulator..."

# Check if virtual environment exists
if [ ! -d ".venv312" ]; then
    echo "❌ Virtual environment .venv312 not found!"
    echo "Please create it first with: python3.12 -m venv .venv312"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv312/bin/activate

# Upgrade pip first
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install psutil with specific version
echo "🚀 Installing psutil..."
pip install "psutil>=5.9.0"

# Verify installation
echo "✅ Verifying psutil installation..."
python -c "import psutil; print(f'psutil version: {psutil.__version__}')"

if [ $? -eq 0 ]; then
    echo "✅ psutil successfully installed!"
else
    echo "❌ psutil installation failed!"
    exit 1
fi

echo "🎉 psutil installation complete!"

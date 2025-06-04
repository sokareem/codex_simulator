#!/bin/bash

echo "🔧 Fixing CodexSimulator installation issues..."

# Make scripts executable
chmod +x install_psutil.sh
chmod +x install_requirements.sh

# Install psutil first
echo "1️⃣ Installing psutil..."
./install_psutil.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed to install psutil"
    exit 1
fi

# Install other requirements
echo "2️⃣ Installing other requirements..."
source .venv312/bin/activate
pip install -r requirements.txt

# Verify critical imports
echo "3️⃣ Verifying critical imports..."
python -c "
import sys
sys.path.insert(0, 'src')

try:
    import psutil
    print('✅ psutil imported successfully')
except ImportError as e:
    print(f'❌ psutil import failed: {e}')

try:
    from codex_simulator.core import StateTracker, AgentFactory, TerminalCrewBuilder
    print('✅ Core modules imported successfully')
except ImportError as e:
    print(f'❌ Core module import failed: {e}')

try:
    from codex_simulator.tools import CSVReaderTool
    print('✅ CSVReaderTool imported successfully')
except ImportError as e:
    print(f'❌ CSVReaderTool import failed: {e}')
"

echo "🎉 Installation fix complete!"
echo "Try running start_with_mcp.sh again"

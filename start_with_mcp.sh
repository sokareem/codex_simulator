#!/bin/bash
# Start CodexSimulator with MCP integration

echo "🚀 Starting CodexSimulator with MCP Integration..."
echo "🔗 Connecting to MCP server at http://localhost:8000"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if MCP server is running
if ! curl -s http://localhost:8000/info > /dev/null 2>&1; then
    echo "❌ MCP server is not running!"
    echo "🔧 Please start the MCP server first:"
    echo "   ./start_mcp_server.sh"
    echo ""
    exit 1
fi

echo "✅ MCP server is running"

# Try to find the correct Python command and environment
PYTHON_CMD=""

# First, try to use the virtual environment if it exists
if [ -f "$SCRIPT_DIR/.venv312/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv312/bin/python"
    echo "✅ Using Python from .venv312"
    # Activate the virtual environment for proper module detection
    source "$SCRIPT_DIR/.venv312/bin/activate"
elif [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    echo "✅ Using Python from .venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    # Check if codex_simulator is available in global Python
    if python3 -c "import codex_simulator" 2>/dev/null; then
        PYTHON_CMD="python3"
        echo "✅ Using global python3 with codex_simulator installed"
    elif python -c "import codex_simulator" 2>/dev/null; then
        PYTHON_CMD="python"
        echo "✅ Using global python with codex_simulator installed"
    else
        # Try running from project directory if available
        if [ -d "$SCRIPT_DIR/src/codex_simulator" ]; then
            echo "🔍 Found project directory, using development mode"
            if command -v python3 &> /dev/null; then
                PYTHON_CMD="python3"
                echo "✅ Using python3 in development mode"
            elif command -v python &> /dev/null; then
                PYTHON_CMD="python"
                echo "✅ Using python in development mode"
            else
                echo "❌ No Python command found!"
                exit 1
            fi
        else
            echo "❌ CodexSimulator not found in any Python environment!"
            echo "🔧 Please ensure CodexSimulator is installed or run from the project directory"
            echo "💡 Try one of these solutions:"
            echo "   1. Install globally: pip install -e ."
            echo "   2. Run from project directory: cd /path/to/codex_simulator && ./start_with_mcp.sh"
            echo "   3. Use virtual environment: source .venv/bin/activate && ./start_with_mcp.sh"
            exit 1
        fi
    fi
fi

# Set environment variables for MCP integration - always include project src in PYTHONPATH
export USE_MCP=true
export MCP_SERVER_URL=http://localhost:8000
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Change to script directory to ensure relative imports work
cd "$SCRIPT_DIR"

# Start CodexSimulator with MCP
echo "🔧 Starting with command: $PYTHON_CMD -m codex_simulator.main"
echo "📁 Working directory: $(pwd)"
echo "🐍 PYTHONPATH: $PYTHONPATH"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🔹 Virtual Environment: $VIRTUAL_ENV"
fi
echo ""

$PYTHON_CMD -m codex_simulator.main

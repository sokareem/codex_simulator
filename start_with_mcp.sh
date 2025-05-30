#!/bin/bash
# Start CodexSimulator with MCP integration

echo "🚀 Starting CodexSimulator with MCP Integration..."
echo "🔗 Connecting to MCP server at http://localhost:8000"
echo ""

# Check if MCP server is running
if ! curl -s http://localhost:8000/info > /dev/null 2>&1; then
    echo "❌ MCP server is not running!"
    echo "🔧 Please start the MCP server first:"
    echo "   ./start_mcp_server.sh"
    echo ""
    exit 1
fi

echo "✅ MCP server is running"

# Set environment variables for MCP integration
export USE_MCP=true
export MCP_SERVER_URL=http://localhost:8000
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Use python3 instead of python for better compatibility
# Also activate the virtual environment if it exists
if [ -f ".venv312/bin/activate" ]; then
    source .venv312/bin/activate
    echo "✅ Activated .venv312 environment"
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Activated .venv environment"
fi

# Start CodexSimulator with MCP using python3
python3 -m codex_simulator.main

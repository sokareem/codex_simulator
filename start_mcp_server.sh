#!/bin/bash
# Start MCP Server for CodexSimulator

echo "🚀 Starting CodexSimulator MCP Server..."
echo "📡 Server will be available at http://localhost:8000"
echo "🔧 Tools will be automatically registered"
echo ""

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the MCP server
python -m codex_simulator.main mcp-server

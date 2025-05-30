#!/bin/bash
# Activation script for CodexSimulator environment

PROJECT_ROOT="/Users/sinmi/Projects/codex_simulator"
VENV_PATH="$PROJECT_ROOT/.venv312"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ CodexSimulator virtual environment not found!"
    echo "Run: ./install_globally.sh"
    exit 1
fi

echo "🚀 Activating CodexSimulator environment..."
source "$VENV_PATH/bin/activate"

echo "✅ Environment activated!"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo ""
echo "Available commands:"
echo "  • terminal_flows - Run terminal assistant with flows"
echo "  • codex-mcp-server - Start MCP server"
echo "  • start_mcp_server.sh - Start MCP server (Terminal 1)"
echo "  • start_with_mcp.sh - Start with MCP (Terminal 2)"
echo ""
echo "To deactivate: deactivate"

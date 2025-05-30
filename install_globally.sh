#!/bin/bash
# Enhanced script to install CodexSimulator globally

set -e  # Exit immediately if a command exits with a non-zero status

# Print with colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}CodexSimulator Global Installation${NC}"
echo -e "${BLUE}===============================================${NC}"

# Check if running with sudo/root when not in a virtual environment
if [[ "$VIRTUAL_ENV" == "" && "$EUID" -ne 0 ]]; then
    echo -e "${YELLOW}This script may need elevated privileges to install globally.${NC}"
    echo -e "${YELLOW}Consider running with sudo if you encounter permission errors.${NC}"
    echo ""
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${BLUE}Installing from: ${SCRIPT_DIR}${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo -e "${BLUE}Using ${PYTHON_VERSION}${NC}"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$python_version < 3.10" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.10+ required. Current version: $python_version"
    exit 1
fi

# Install dependencies and package
echo -e "${BLUE}Installing package and dependencies...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install -e "$SCRIPT_DIR"

# Verify installation
if command -v terminal_flows &> /dev/null; then
    echo -e "${GREEN}✓ Installation successful!${NC}"
    echo -e "${GREEN}✓ 'terminal_flows' command is now available globally${NC}"
else
    echo -e "${YELLOW}⚠️ Installation completed but 'terminal_flows' command is not in PATH.${NC}"
    
    # Find the location of the installed command
    SITE_PACKAGES=$(python3 -m pip show codex_simulator | grep Location | cut -d ' ' -f 2)
    BIN_DIR=$(dirname $(dirname "$SITE_PACKAGES"))/bin
    
    if [[ -f "$BIN_DIR/terminal_flows" ]]; then
        echo -e "${YELLOW}The command is installed at: $BIN_DIR/terminal_flows${NC}"
        echo -e "${YELLOW}Consider adding this directory to your PATH:${NC}"
        echo -e "${YELLOW}    export PATH=\"$BIN_DIR:\$PATH\"${NC}"
    fi
fi

# Create symbolic links for convenience if in common bin directory
if [[ -d "/usr/local/bin" && -w "/usr/local/bin" ]]; then
    echo -e "${BLUE}Creating convenience command 'codex-terminal'...${NC}"
    if command -v terminal_flows &> /dev/null; then
        TERMINAL_PATH=$(which terminal_flows)
        ln -sf "$TERMINAL_PATH" "/usr/local/bin/codex-terminal"
        echo -e "${GREEN}✓ You can now use 'codex-terminal' from anywhere${NC}"
    fi
fi

# Create global command aliases
echo "Creating global command aliases..."

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi

echo "✅ CodexSimulator installed globally!"
echo "🔧 Available commands:"
echo "   codex-terminal - Main terminal assistant"
echo "   codex-mcp-server - Start MCP server"

echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Available commands after installation:${NC}"
echo -e "${BLUE}terminal_flows${NC} - Run the terminal assistant with flow orchestration"
echo -e "${BLUE}terminal_assistant${NC} - Run the terminal assistant in basic mode"
echo -e "${BLUE}hybrid_mode${NC} - Run the assistant with automatic flow/crew selection"
echo -e "${BLUE}codex-terminal${NC} - Convenience command (if symbolic link was created)"
echo -e "${GREEN}===============================================${NC}"
echo -e "${YELLOW}NOTE: Location features are now available in the terminal!${NC}"
echo -e "${YELLOW}Try commands like:${NC}"
echo -e "${YELLOW}- 'set my location to San Francisco'${NC}"
echo -e "${YELLOW}- 'add location New York as work'${NC}"
echo -e "${YELLOW}- 'where am I?'${NC}"
echo -e "${YELLOW}- 'find coffee shops near me'${NC}"
echo -e "${GREEN}===============================================${NC}"

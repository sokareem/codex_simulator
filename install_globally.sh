#!/bin/bash
# Enhanced script to install CodexSimulator globally with Python 3.12 support

set -e  # Exit immediately if a command exits with a non-zero status

# Print with colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}CodexSimulator Global Installation with Python 3.12${NC}"
echo -e "${BLUE}===============================================${NC}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${BLUE}Installing from: ${SCRIPT_DIR}${NC}"

# Function to find Python 3.12
find_python312() {
    local possible_commands=(
        'python3.12'
        'python3'
        '/usr/bin/python3.12'
        '/usr/local/bin/python3.12'
        '/opt/homebrew/bin/python3.12'
        '/Users/sinmi/miniconda3/bin/python3.12'
        '/Users/sinmi/miniconda3/envs/py312/bin/python'
    )
    
    for cmd in "${possible_commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            local version_output=$("$cmd" --version 2>&1)
            if [[ "$version_output" == *"Python 3.12"* ]]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Check for Python 3.12 and set up environment
PYTHON_CMD=""
VENV_PATH="$SCRIPT_DIR/.venv312"

echo -e "${BLUE}Setting up Python 3.12 environment...${NC}"

# Try to find Python 3.12
if PYTHON_CMD=$(find_python312); then
    echo -e "${GREEN}✅ Found Python 3.12: $PYTHON_CMD${NC}"
else
    echo -e "${YELLOW}⚠️ Python 3.12 not found. Checking for compatible Python...${NC}"
    
    # Fallback to any available Python 3.10+
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if (( $(echo "$python_version >= 3.10" | bc -l) )); then
            echo -e "${YELLOW}Using Python $python_version (minimum 3.10 required)${NC}"
        else
            echo -e "${RED}❌ Python 3.10+ required. Current version: $python_version${NC}"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        python_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if (( $(echo "$python_version >= 3.10" | bc -l) )); then
            echo -e "${YELLOW}Using Python $python_version (minimum 3.10 required)${NC}"
        else
            echo -e "${RED}❌ Python 3.10+ required. Current version: $python_version${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ No suitable Python found!${NC}"
        echo -e "${RED}Please install Python 3.10+ and ensure it's available in your PATH.${NC}"
        exit 1
    fi
fi

# Check if we should create/use virtual environment
USE_VENV=false
if [[ "$PYTHON_CMD" == *"python3.12"* ]] || [[ "$VIRTUAL_ENV" == "" ]]; then
    USE_VENV=true
    echo -e "${BLUE}Setting up virtual environment for isolated installation...${NC}"
    
    # Remove existing venv if it exists
    if [ -d "$VENV_PATH" ]; then
        echo -e "${YELLOW}🗑️ Removing existing .venv312 environment${NC}"
        rm -rf "$VENV_PATH"
    fi
    
    # Create virtual environment
    echo -e "${BLUE}🔨 Creating virtual environment at $VENV_PATH${NC}"
    if ! "$PYTHON_CMD" -m venv "$VENV_PATH"; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    
    # Update PYTHON_CMD to use venv python
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        PYTHON_CMD="$VENV_PATH/Scripts/python"
        PIP_CMD="$VENV_PATH/Scripts/pip"
    else
        # Unix/Linux/macOS
        PYTHON_CMD="$VENV_PATH/bin/python"
        PIP_CMD="$VENV_PATH/bin/pip"
    fi
    
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    # Use system Python and pip
    PIP_CMD="$PYTHON_CMD -m pip"
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${BLUE}Using ${PYTHON_VERSION} (command: ${PYTHON_CMD})${NC}"

# Check if running with sudo/root when not in a virtual environment
if [[ "$USE_VENV" == "false" && "$VIRTUAL_ENV" == "" && "$EUID" -ne 0 ]]; then
    echo -e "${YELLOW}This script may need elevated privileges to install globally.${NC}"
    echo -e "${YELLOW}Consider running with sudo if you encounter permission errors.${NC}"
    echo ""
fi

# Install dependencies and package
echo -e "${BLUE}Installing package and dependencies...${NC}"

# Set pip install options
PIP_INSTALL_OPTS=""
if [[ "$USE_VENV" == "false" && "$VIRTUAL_ENV" == "" && "$EUID" -ne 0 ]]; then
    PIP_INSTALL_OPTS="--user --break-system-packages"
    echo -e "${YELLOW}Running pip install with --user flag as not in venv and not root.${NC}"
elif [[ "$USE_VENV" == "false" ]]; then
    PIP_INSTALL_OPTS="--break-system-packages"
fi

# Upgrade pip first
echo -e "${BLUE}📦 Upgrading pip...${NC}"
$PIP_CMD install --upgrade pip $PIP_INSTALL_OPTS

# Install compatible dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
$PIP_CMD install $PIP_INSTALL_OPTS \
    "pydantic>=2.4.2,<3.0.0" \
    "crewai[tools]>=0.86.0,<1.0.0" \
    "langchain-core>=0.1.0,<0.3.0" \
    "langchain-google-genai>=0.0.1,<2.0.0" \
    "google-generativeai>=0.3.0,<1.0.0" \
    "python-dotenv>=1.0.0" \
    "requests>=2.28.0" \
    "beautifulsoup4>=4.12.0" \
    "typing-extensions>=4.6.1" \
    "annotated-types>=0.6.0" \
    "pypdf>=4.0.0" \
    "langchain-text-splitters>=0.0.1" \
    "matplotlib>=3.5.0" \
    "psutil>=5.9.0" \
    "GitPython>=3.1.0" \
    "bandit>=1.7.0"

# Install the project in development mode
echo -e "${BLUE}📦 Installing CodexSimulator...${NC}"
$PIP_CMD install -e "$SCRIPT_DIR" $PIP_INSTALL_OPTS

# Create enhanced activation script if using venv
if [[ "$USE_VENV" == "true" ]]; then
    ACTIVATION_SCRIPT="$SCRIPT_DIR/activate_codex.sh"
    cat > "$ACTIVATION_SCRIPT" << EOF
#!/bin/bash
# Activation script for CodexSimulator environment

PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="\$PROJECT_ROOT/.venv312"

if [ ! -d "\$VENV_PATH" ]; then
    echo "❌ CodexSimulator virtual environment not found!"
    echo "Run: ./install_globally.sh"
    exit 1
fi

echo "🚀 Activating CodexSimulator environment..."
source "\$VENV_PATH/bin/activate"

echo "✅ Environment activated!"
echo "Python version: \$(python --version)"
echo "Current directory: \$(pwd)"
echo ""
echo "Available commands:"
echo "  • terminal_flows - Run terminal assistant with flows"
echo "  • codex-mcp-server - Start MCP server"
echo "  • start_mcp_server.sh - Start MCP server (Terminal 1)"
echo "  • start_with_mcp.sh - Start with MCP (Terminal 2)"
echo ""
echo "To deactivate: deactivate"
EOF
    chmod +x "$ACTIVATION_SCRIPT"
    echo -e "${GREEN}✅ Created activation script: $ACTIVATION_SCRIPT${NC}"
fi

# Verify installation
BIN_DIR_CALCULATED=false
BIN_DIR=""

# Function to calculate BIN_DIR if not already done
calculate_bin_dir() {
    if [ "$BIN_DIR_CALCULATED" = false ]; then
        if [[ "$USE_VENV" == "true" ]]; then
            # Using virtual environment
            if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
                BIN_DIR="$VENV_PATH/Scripts"
            else
                BIN_DIR="$VENV_PATH/bin"
            fi
        else
            # Using system Python
            SITE_PACKAGES=$($PYTHON_CMD -m pip show codex_simulator | grep Location | cut -d ' ' -f 2)
            if [ -n "$SITE_PACKAGES" ]; then
                BIN_DIR=$(dirname $(dirname "$SITE_PACKAGES"))/bin
            else
                if [[ "$EUID" -eq 0 ]]; then
                    BIN_DIR="/usr/local/bin"
                else
                    BIN_DIR="$HOME/.local/bin"
                fi # This 'fi' closes the 'if [[ "$EUID" -eq 0 ]]'
            fi # This 'fi' closes the 'if [ -n "$SITE_PACKAGES" ]'
        fi # This 'fi' closes the 'if [[ "$USE_VENV" == "true" ]]'
        BIN_DIR_CALCULATED=true
    fi # This 'fi' closes the 'if [ "$BIN_DIR_CALCULATED" = false ]'
}

# Update shell scripts to use the correct Python environment
update_shell_scripts() {
    local target_bin_dir="$1" # e.g., /usr/local/bin
    local script_name="$2"    # e.g., start_mcp_server.sh
    # SCRIPT_DIR is the location of install_globally.sh, which is the project root
    local original_project_dir="$SCRIPT_DIR" 
    # PYTHON_CMD is the Python interpreter determined by install_globally.sh (e.g., .venv312/bin/python)
    local python_to_use="$PYTHON_CMD" 

    local source_script_path="$original_project_dir/$script_name"
    local target_script_path="$target_bin_dir/$script_name"

    if [ -f "$source_script_path" ]; then
        # Extract the arguments passed to "codex_simulator.main" from the original script
        # Example: $PYTHON_CMD -m codex_simulator.main mcp-server
        main_command_line=$(grep -E '\$PYTHON_CMD -m codex_simulator.main' "$source_script_path" | tail -n 1)
        app_args=$(echo "$main_command_line" | sed 's/.*codex_simulator.main//' | xargs) # xargs to trim whitespace

        cat > "$target_script_path" << EOF
#!/bin/bash
# Globally installed version of $script_name
# Original project location (for module resolution): $original_project_dir
# Python executable: $python_to_use

echo "🚀 Running $script_name (Globally Installed Version from $target_script_path)"
echo "💡 This script will operate in your current working directory: \$(pwd)"

PROJECT_INSTALL_DIR="$original_project_dir" # Renamed for clarity
PYTHON_EXEC="$python_to_use"

if [ ! -f "\$PYTHON_EXEC" ]; then
    echo -e "\033[0;31m❌ Python executable not found: \$PYTHON_EXEC\033[0m"
    echo -e "\033[1;33m💡 Please try re-installing CodexSimulator from \$PROJECT_INSTALL_DIR using ./install_globally.sh\033[0m"
    exit 1
fi

# Set PYTHONPATH to include the project's src directory for module imports
export PYTHONPATH="\$PROJECT_INSTALL_DIR/src:\$PYTHONPATH"

# DO NOT cd to PROJECT_INSTALL_DIR. The script should operate in the user's current directory.
# The Python application (codex_simulator.main) will use os.getcwd() which will be the invocation directory.

echo "🔧 Executing: \$PYTHON_EXEC -m codex_simulator.main $app_args"
echo "📁 Working directory for Python process: \$(pwd)"
echo "🐍 PYTHONPATH: \$PYTHONPATH"
if [[ -n "\$VIRTUAL_ENV" ]]; then
    # This VIRTUAL_ENV is the one active in the user's shell, if any.
    # The script itself uses PYTHON_EXEC from the installation.
    echo "🌐 Active Shell Virtual Environment: \$VIRTUAL_ENV (Note: This script uses its own configured Python: \$PYTHON_EXEC)"
fi
echo ""

\$PYTHON_EXEC -m codex_simulator.main $app_args
EOF
        chmod +x "$target_script_path"
        echo -e "${GREEN}✅ $script_name (global version) installed to $target_script_path${NC}"
    else
        echo -e "${RED}❌ Source script $source_script_path not found.${NC}"
    fi
}

# Verify command availability and install scripts
if [[ "$USE_VENV" == "true" ]]; then
    calculate_bin_dir
    if [ -f "$BIN_DIR/terminal_flows" ]; then
        echo -e "${GREEN}✓ 'terminal_flows' command available in virtual environment${NC}"
    else
        echo -e "${YELLOW}⚠️ 'terminal_flows' command not found in virtual environment${NC}"
    fi
    
    if [ -f "$BIN_DIR/codex-mcp-server" ]; then
        echo -e "${GREEN}✓ 'codex-mcp-server' command available in virtual environment${NC}"
    else
        echo -e "${YELLOW}⚠️ 'codex-mcp-server' command not found in virtual environment${NC}"
    fi
    
else
    # Check global commands
    if command -v terminal_flows &> /dev/null; then
        echo -e "${GREEN}✓ 'terminal_flows' command is now available globally.${NC}"
    else
        echo -e "${YELLOW}⚠️ 'terminal_flows' command is not in PATH after installation.${NC}"
        calculate_bin_dir
        if [ -n "$BIN_DIR" ] && [ -f "$BIN_DIR/terminal_flows" ]; then
            echo -e "${YELLOW}The command 'terminal_flows' is installed at: $BIN_DIR/terminal_flows${NC}"
            echo -e "${YELLOW}Consider adding this directory to your PATH:${NC}"
            echo -e "${YELLOW}    export PATH=\"$BIN_DIR:\$PATH\"${NC}"
        fi
    fi

    if command -v codex-mcp-server &> /dev/null; then
        echo -e "${GREEN}✓ 'codex-mcp-server' command is now available globally.${NC}"
    else
        echo -e "${YELLOW}⚠️ 'codex-mcp-server' command is not in PATH after installation.${NC}"
        calculate_bin_dir
        if [ -n "$BIN_DIR" ] && [ -f "$BIN_DIR/codex-mcp-server" ]; then
            echo -e "${YELLOW}The command 'codex-mcp-server' is installed at: $BIN_DIR/codex-mcp-server${NC}"
        fi
    fi
fi

# Install MCP shell scripts
if [[ -d "/usr/local/bin" && -w "/usr/local/bin" ]]; then
    echo -e "${BLUE}Installing MCP shell scripts globally...${NC}"
    update_shell_scripts "/usr/local/bin" "start_mcp_server.sh"
    update_shell_scripts "/usr/local/bin" "start_with_mcp.sh"
    
    # Create convenience command if not using venv
    if [[ "$USE_VENV" == "false" ]] && command -v terminal_flows &> /dev/null; then
        echo -e "${BLUE}Creating convenience command 'codex-terminal'...${NC}"
        TERMINAL_PATH=$(which terminal_flows)
        ln -sf "$TERMINAL_PATH" "/usr/local/bin/codex-terminal"
        echo -e "${GREEN}✓ You can now use 'codex-terminal' from anywhere${NC}"
    fi
else
    # Install to user's local bin
    echo -e "${BLUE}Installing MCP shell scripts to user's local bin...${NC}"
    USER_BIN_DIR="$HOME/.local/bin"
    mkdir -p "$USER_BIN_DIR"
    
    update_shell_scripts "$USER_BIN_DIR" "start_mcp_server.sh"
    update_shell_scripts "$USER_BIN_DIR" "start_with_mcp.sh"
fi

# Create global command aliases
echo "Creating global command aliases..."

# Add to PATH if not already there
# This ensures ~/.local/bin is in PATH, which is a common target for user-level pip installs
EXPECTED_BIN_PATH="$HOME/.local/bin"
if [[ -d "$EXPECTED_BIN_PATH" && ":$PATH:" != *":$EXPECTED_BIN_PATH:"* ]]; then
    echo -e "${BLUE}Adding $EXPECTED_BIN_PATH to PATH for user shells (bash/zsh)...${NC}"
    # Ensure the directory exists before adding to PATH scripts
    mkdir -p "$EXPECTED_BIN_PATH"
    
    SHELL_CONFIG_FILES=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile")
    EXPORT_LINE="export PATH=\"\$HOME/.local/bin:\$PATH\""

    for config_file in "${SHELL_CONFIG_FILES[@]}"; do
        if [ -f "$config_file" ] || [ "$config_file" == "$HOME/.profile" ] || [ "$config_file" == "$HOME/.bash_profile" ]; then # Also attempt to create .profile or .bash_profile if they don't exist but are common
            if ! grep -qF -- "$EXPORT_LINE" "$config_file" 2>/dev/null ; then
                echo -e "\n# Added by CodexSimulator installer\n$EXPORT_LINE" >> "$config_file"
                echo -e "${GREEN}✓ Added $EXPECTED_BIN_PATH to $config_file${NC}"
            else
                echo -e "${YELLOW}✓ $EXPECTED_BIN_PATH already in $config_file PATH configuration.${NC}"
            fi
        fi
    done
    echo -e "${YELLOW}Please reload your shell (e.g., 'source ~/.bashrc', 'source ~/.zshrc') or open a new terminal for PATH changes to take effect.${NC}"
fi

echo "✅ CodexSimulator installed successfully!"
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Installation Summary:${NC}"

if [[ "$USE_VENV" == "true" ]]; then
    echo -e "${BLUE}🐍 Using Virtual Environment: $VENV_PATH${NC}"
    echo -e "${BLUE}📁 Project Directory: $SCRIPT_DIR${NC}"
    echo -e "${BLUE}👉 To activate this venv for development, run from project directory:${NC}"
    echo -e "${YELLOW}     cd $SCRIPT_DIR && source activate_codex.sh${NC}"
    echo -e "${BLUE}   Then use: terminal_flows, codex-mcp-server, etc., or run python scripts directly.${NC}"
else
    echo -e "${BLUE}🐍 Using System Python: $PYTHON_CMD${NC}"
fi

echo -e "${YELLOW}Globally available commands (should work from any directory):${NC}"
echo -e "${BLUE}  • terminal_flows${NC} - Terminal assistant with flows"
echo -e "${BLUE}  • codex-mcp-server${NC} - Start MCP server (via Python entry point)"
echo -e "${BLUE}  • start_mcp_server.sh${NC} - Start MCP server (shell script, typically in /usr/local/bin or ~/.local/bin)"
echo -e "${BLUE}  • start_with_mcp.sh${NC} - Start with MCP (shell script, typically in /usr/local/bin or ~/.local/bin)"
echo -e "${GREEN}===============================================${NC}"
echo -e "${YELLOW}NOTE: To use MCP integration, run in separate terminals:${NC}"
echo -e "${YELLOW}Terminal 1: start_mcp_server.sh${NC}"
echo -e "${YELLOW}Terminal 2: start_with_mcp.sh${NC}"
echo -e "${GREEN}===============================================${NC}"

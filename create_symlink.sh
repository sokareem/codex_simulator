#!/bin/bash

# Create a wrapper script in the user's bin directory
WRAPPER_PATH="$HOME/bin/codex_simulator"

mkdir -p "$HOME/bin"

cat > "$WRAPPER_PATH" << 'EOF'
#!/bin/bash

# Get the path to this script
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The actual project directory
PROJECT_DIR="/Users/sinmi/Projects/codex_simulator"

# Change to the project directory and run the command
cd "$PROJECT_DIR"
crewai run "$@"
EOF

chmod +x "$WRAPPER_PATH"

# Check if $HOME/bin is in PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bash_profile"
  echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
  echo "Added $HOME/bin to your PATH in .bash_profile and .zshrc"
  echo "Please restart your terminal or run 'source ~/.bash_profile' or 'source ~/.zshrc'"
fi

echo "Created symlink at $WRAPPER_PATH"
echo "You can now run 'codex_simulator' from any directory."

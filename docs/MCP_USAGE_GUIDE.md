# MCP Integration Usage Guide

## Quick Start (Recommended)

### Option 1: Automatic Setup
```bash
# 1. Install MCP dependencies
python install_mcp_deps.py

# 2. Make scripts executable
chmod +x start_mcp_server.sh start_with_mcp.sh

# 3. Start MCP server (Terminal 1)
./start_mcp_server.sh

# 4. Start CodexSimulator with MCP (Terminal 2)
./start_with_mcp.sh
```

### Option 2: Manual Setup
```bash
# Terminal 1: Start MCP Server
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m codex_simulator.main mcp-server

# Terminal 2: Start CodexSimulator with MCP
export USE_MCP=true
export MCP_SERVER_URL=http://localhost:8000
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m codex_simulator.main
```

### Option 3: Development Mode
```python
# In Python script or Jupyter notebook
import os
os.environ['USE_MCP'] = 'true'
os.environ['MCP_SERVER_URL'] = 'http://localhost:8000'

from codex_simulator.main import run_terminal_assistant_with_flows
run_terminal_assistant_with_flows()
```

## Verification

When MCP is working correctly, you'll see:
```
🚀 Starting CodexSimulator with Flow orchestration...
🔗 MCP integration enabled - Server: http://localhost:8000
✅ MCP client connected to http://localhost:8000
💻 Enter command (or 'quit' to exit):
```

## MCP Server Management

### Check Server Status
```bash
curl http://localhost:8000/info
```

### View Available Tools
```bash
curl http://localhost:8000/info | jq '.supported_tools'
```

### Server Logs
The MCP server provides detailed logging for debugging:
- Tool invocations with execution times
- Context updates and fetches
- Client connections and disconnections
- Error messages with stack traces

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   ❌ Failed to connect to MCP server: Connection refused
   ```
   **Solution**: Ensure MCP server is running first

2. **Tool Not Found**
   ```
   Error: Tool 'my_tool' not found in registry
   ```
   **Solution**: Check tool registration in server startup

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Solution**: Run `python install_mcp_deps.py`

4. **Port Already in Use**
   ```
   OSError: [Errno 48] Address already in use
   ```
   **Solution**: Kill existing process or use different port
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

### Debugging Mode

Enable debug logging:
```bash
export DEBUG=1
export MCP_LOG_LEVEL=DEBUG
```

### Fallback Mode

If MCP fails, CodexSimulator automatically falls back to direct mode:
```
⚠️ Failed to connect to MCP server: Connection refused
Falling back to direct tool execution
```

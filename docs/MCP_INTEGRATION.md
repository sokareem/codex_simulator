# Model Context Protocol (MCP) Integration

The CodexSimulator now supports the Model Context Protocol (MCP) for enhanced agent communication, tool sharing, and context management across distributed environments.

## Overview

MCP integration provides:
- **Centralized Tool Registry**: Tools are registered on the MCP server and accessible to all agents
- **Shared Context Management**: Session state, command history, and user preferences are synchronized
- **Distributed Agent Communication**: Agents can communicate through the MCP protocol
- **Load Balancing**: Multiple MCP servers can be used for scalability
- **Fallback Mechanisms**: Graceful degradation when MCP is unavailable

## Quick Start

### 1. Start MCP Server

```bash
# Terminal 1: Start MCP server
python -m codex_simulator.mcp.server
```

The server will start on `http://localhost:8000` by default.

### 2. Run CodexSimulator with MCP

```bash
# Terminal 2: Run CodexSimulator with MCP enabled
python -c "
from codex_simulator.main import run_terminal_assistant_with_flows
import os
os.environ['USE_MCP'] = 'true'
os.environ['MCP_SERVER_URL'] = 'http://localhost:8000'
run_terminal_assistant_with_flows()
"
```

### 3. Verify MCP Integration

Once both are running, you'll see:

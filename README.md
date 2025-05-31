<<<<<<< HEAD
# codex_simulator
=======
# CodexSimulator: Advanced AI-Powered Terminal Assistant

## Abstract

CodexSimulator is a sophisticated, AI-driven terminal assistant built using the CrewAI framework. It orchestrates a team of specialized AI agents to understand and execute complex commands given in natural language. This tool provides an interactive command-line interface for a wide range of tasks, including file system navigation, file content manipulation, code execution, web research, PDF document analysis, and more. CodexSimulator aims to enhance developer productivity by offering an intelligent and conversational way to interact with their system and access information. It features multiple operational modes, including a robust flow-based orchestration for complex queries and an optional Model Context Protocol (MCP) integration for advanced, potentially distributed, agent collaboration.

## Key Features

*   **Natural Language Understanding:** Interact with your terminal using conversational commands.
*   **Multi-Agent System:** Leverages a crew of specialized AI agents (e.g., File Navigator, Code Executor, Web Researcher, PDF Analyst) for targeted task execution.
*   **CrewAI Framework:** Built on CrewAI for robust agent and task management.
*   **Flow Orchestration:** Employs `crewai.Flow` for advanced workflow management, enabling conditional routing and handling of complex, multi-step commands.
*   **Hybrid Execution Mode:** Intelligently switches between direct crew execution for simple commands and flow orchestration for more complex ones.
*   **Model Context Protocol (MCP) Support:** Optional integration with MCP for dynamic tool access, context sharing, and unified message routing, paving the way for more scalable and distributed agent systems.
*   **Safe Tool Usage:** Prioritizes safety with tools like `SafeShellTool` that operate with command whitelists and other security measures.
*   **Persistent Memory:** Utilizes a `CLAUDE.md` file in the working directory to maintain command history, context, and operational logs.
*   **Configurable LLMs:** Primarily designed for Google's Gemini models, configurable via environment variables.
*   **Extensible Toolset:** Comes with a variety of built-in tools and can be extended with new custom tools.
*   **Report Generation:** Capable of generating reports on specified topics using its research and reporting agents.

## Architecture Overview

CodexSimulator's architecture is designed for modularity and extensibility.

*   **Core Components:**
    *   `CodexSimulator (crew.py)`: The main class orchestrating agent interactions, state management, and task execution.
    *   `TerminalAssistantFlow (flows/terminal_flow.py)`: A flow-based system for routing commands to appropriate handlers and managing complex interactions.
    *   `StateTracker`: Manages the application's state, including current working directory (CWD) and command history.
    *   `CLAUDE.md`: A dynamically updated Markdown file in the CWD serving as a persistent memory, logging interactions and results.
*   **Agent Roles:**
    *   `TerminalCommander`: The primary orchestrator agent that interprets user commands and delegates tasks to specialist agents.
    *   `FileNavigator`: Specializes in file system operations (listing files, reading files, navigation).
    *   `CodeExecutor`: Securely executes code snippets and shell commands using whitelisted operations.
    *   `WebResearcher`: Performs internet searches and fetches web content.
    *   `PDFDocumentAnalyst`: Reads, analyzes, and extracts information from PDF documents.
    *   `PerformanceMonitor`: Profiles execution metrics and system information.
*   **Execution Modes:**
    *   **Crew Mode:** Direct execution of tasks by specialized CrewAI agents. Suitable for simpler, well-defined commands.
    *   **Flow Mode:** Utilizes `crewai.Flow` to orchestrate tasks through a graph-based workflow, allowing for conditional logic and more complex command processing. This is the default for terminal interaction.
    *   **Hybrid Mode:** Dynamically assesses command complexity and chooses between Crew Mode and Flow Mode.

## Installation

### Prerequisites

*   Python (version >= 3.10 and <= 3.13)
*   Git
*   Access to a Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/codex_simulator.git # Replace with your repo URL
cd codex_simulator
```

### 2. Set Up the Environment

It's highly recommended to use a virtual environment.

```bash
python3 -m venv .venv # Or .venv312 for Python 3.12 specifically
source .venv/bin/activate
```

### 3. Install Dependencies

The project uses `pip` for dependency management.

```bash
pip install -e .
# This installs the package in editable mode and its dependencies from setup.py
# For MCP-specific dependencies (if you plan to use MCP):
# pip install -e ".[mcp]" # Assuming you have an [mcp] extra in setup.py or pyproject.toml
# Alternatively, ensure all dependencies from pyproject.toml are installed.
```
You might also find an `install_globally.sh` script in the repository which attempts to automate some of these steps, including creating command aliases. Review it before running.

### 4. Environment Variables

Create a `.env` file in the root of the project directory:

```env
# .env
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
MODEL="gemini-1.5-flash-latest" # Or your preferred Gemini model

# For SerpAPI (if used by WebResearcher)
# SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY"

# For MCP (if you plan to use it)
# USE_MCP="false" # Set to "true" to enable MCP
# MCP_SERVER_URL="http://localhost:8000"
```

Replace `YOUR_GEMINI_API_KEY` with your actual API key.

## Running CodexSimulator

Ensure your virtual environment is activated (`source .venv/bin/activate`).

### Default Mode (Terminal Assistant with Flows)

This is the primary way to interact with CodexSimulator. It uses flow orchestration.

```bash
python -m codex_simulator.main
```
or if the `codex-terminal` alias was set up during installation:
```bash
codex-terminal
```
You can also run it directly:
```bash
python src/codex_simulator/main.py
```

### Report Generation Mode

To generate a report on a specific topic:

```bash
python -m codex_simulator.main --mode report --topic "Quantum Computing Advancements"
```
Or using the `codex-simulator` entry point:
```bash
codex-simulator --mode report --topic "AI in Healthcare"
```
The report will be saved as `report.md`.

### Hybrid Mode

This mode intelligently selects between direct crew execution and flow orchestration based on command complexity.

```bash
python -m codex_simulator.main hybrid_mode
```
Or using the `hybrid_mode` entry point (if defined in `pyproject.toml` and installed):
```bash
hybrid_mode
```

### Using with Model Context Protocol (MCP)

MCP allows for more advanced and potentially distributed agent operations.

**1. Start the MCP Server (Terminal 1)**

You can start the standalone MCP server using:
```bash
python -m codex_simulator.main mcp-server
```
Or, if the alias `codex-mcp-server` is available:
```bash
codex-mcp-server
```
A shell script `start_mcp_server.sh` might also be available for convenience.
The server typically runs on `http://localhost:8000`.

**2. Run CodexSimulator with MCP Enabled (Terminal 2)**

Set the following environment variables before running:
```bash
export USE_MCP=true
export MCP_SERVER_URL="http://localhost:8000" # Or your MCP server URL
```
Then run the terminal assistant as usual:
```bash
python -m codex_simulator.main
```
A shell script `start_with_mcp.sh` might also be available to simplify this.
Refer to `docs/MCP_USAGE_GUIDE.md` for more detailed MCP setup instructions.

### Other Development Commands

The `pyproject.toml` and `main.py` define other entry points which can be useful for development:

*   **Train Crew:**
    ```bash
    # Example: python -m codex_simulator.main train 5 training_output.json
    python -m codex_simulator.main train <n_iterations> <output_filename>
    ```
*   **Replay Crew Execution:**
    ```bash
    python -m codex_simulator.main replay <task_id>
    ```
*   **Test Crew Execution:**
    ```bash
    # Example: python -m codex_simulator.main test 3 gemini-1.5-pro
    python -m codex_simulator.main test <n_iterations> <eval_llm_model_name>
    ```

## How It Works: The Making of CodexSimulator

CodexSimulator is more than just a command-line tool; it's an exploration into building sophisticated AI assistants. Here's a glimpse into its core:

*   **Leveraging CrewAI:** At its heart, CodexSimulator uses the CrewAI framework. This provides the foundational structure for defining agents, their roles, tools, and tasks, and for orchestrating their collaboration.

*   **The Power of Specialized Agents:** Instead of a single monolithic AI, CodexSimulator employs a "crew" of specialized agents. Each agent (e.g., `FileNavigator`, `CodeExecutor`, `WebResearcher`, `PDFDocumentAnalyst`) is an expert in its domain, equipped with specific tools and knowledge. The `TerminalCommander` agent acts as the manager, decomposing user requests and delegating to the appropriate specialist.

*   **Sophisticated Tooling:** Agents are equipped with a variety of tools to perform actions. These range from safe shell execution (`SafeShellTool`) and file system operations (`SafeDirectoryTool`, `SafeFileReadTool`, `SafeFileWriteTool`) to web searching (`SerpAPITool`, `WebsiteTool`) and PDF analysis (`PDFReaderTool`). Safety is a key consideration, with tools often having built-in restrictions (e.g., command whitelists).

*   **Flow Orchestration for Complex Tasks:** For handling complex or ambiguous user commands, CodexSimulator utilizes `crewai.Flow`. This allows for defining workflows where the output of one task can conditionally trigger others, enabling more nuanced and multi-step command processing than a simple sequential task execution.

*   **Model Context Protocol (MCP) for Scalability:** The integration of MCP (experimental) opens doors for more advanced agent interactions. MCP allows tools and context to be shared across agents, potentially even those running in different processes or machines. This is a step towards building more distributed and scalable AI systems.

*   **Memory and Context Management (`CLAUDE.md`):** To provide a coherent and context-aware experience, CodexSimulator maintains a "memory" in the `CLAUDE.md` file. This file, located in the current working directory, logs commands, their results, and changes in state (like CWD). This allows the assistant to "remember" previous interactions within a session and across sessions if working in the same directory.

*   **Safety First:** A significant effort has gone into making interactions safe, especially when executing code or file system commands. Tools like `SafeShellTool` are designed with whitelists of allowed commands and blocked patterns to prevent accidental or malicious operations.

This project represents a continuous effort to explore the capabilities of multi-agent AI systems in practical, developer-focused applications.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report issues, or suggest new features.

(Consider adding more specific contribution guidelines if you wish, e.g., coding standards, testing procedures.)

## License

(Specify your project's license here, e.g., MIT License, Apache 2.0.)
>>>>>>> feature/rebased-mcp-codex_simulator

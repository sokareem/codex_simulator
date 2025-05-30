# CodexSimulator Crew

Welcome to the CodexSimulator Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `GEMINI_API_KEY` into the `.env` file for the primary LLM.**

- Modify `src/codex_simulator/config/agents.yaml` to define your agents
- Modify `src/codex_simulator/config/tasks.yaml` to define your tasks
- Modify `src/codex_simulator/crew.py` to add your own logic, tools and specific args
- Modify `src/codex_simulator/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the codex_simulator Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The codex_simulator Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Model Context Protocols (MCP) Integration Roadmap

We will introduce a dedicated MCP server–client layer to enable dynamic tool access, context sharing, and unified message routing across agents. The refactor plan:

1. Create a feature branch  
   - `git checkout -b feature/mcp-integration`  
2. Define MCP communication contracts  
   - Design JSON/RPC schemas for `invoke_tool`, `fetch_context`, `update_state`  
   - Version schemas under `src/codex_simulator/mcp/schemas.py`  
3. Implement MCP server  
   - Stand up an async HTTP or WebSocket server in `src/codex_simulator/mcp/server.py`  
   - Expose endpoints for tool requests and context queries  
4. Build MCP client adapter  
   - In each Agent factory (`crew.py`), wrap `SafeShellTool`, `WebResearcher`, etc., to route through MCP client  
   - Place client logic in `src/codex_simulator/mcp/client.py`  
5. Migrate delegation logic  
   - Refactor `DelegateTool` to use MCP client for dispatching subtasks instead of direct local calls  
6. Update flows and crews  
   - Inject MCP client into `TerminalAssistantFlow` and `CrewFactory` contexts  
   - Adjust `kickoff` inputs to include `mcp_url` and credentials  
7. Testing & validation  
   - Add unit tests for MCP schemas and client tooling  
   - End-to-end test: spawn MCP server in CI, execute sample workflows, verify correct delegation and context updates  
8. Documentation & examples  
   - Update README with usage examples: how to start MCP server, switch between direct vs MCP modes  
   - Provide sample commands and expected JSON exchanges  
9. Release & versioning  
   - Bump package version, tag `v1.0.0-mcp`  
   - Publish MCP extension notes in CHANGELOG.md

## Support

For support, questions, or feedback regarding the CodexSimulator Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.

# Claude Code Terminal Assistant - Development Guide

This document provides a comprehensive guide to the Claude Code Terminal Assistant, a terminal-based AI assistant built with CrewAI that helps with file system navigation, code execution, and web research.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Agent System](#agent-system)
4. [LLM Integration](#llm-integration)
5. [Safety Measures](#safety-measures)
6. [Development Steps](#development-steps)
7. [Troubleshooting](#troubleshooting)
8. [Future Enhancements](#future-enhancements)

## Project Overview

The Claude Code Terminal Assistant is a terminal-based AI assistant that can:
- Navigate the file system
- Execute code and shell commands
- Perform web searches
- Respond to natural language queries

It uses a multi-agent system orchestrated through CrewAI where each agent specializes in a particular domain.

## Architecture

### High-Level Architecture

The Claude Code Terminal Assistant is structured around a modular design, with distinct components handling specific responsibilities:

1.  **Main CLI Application (`claude_terminal.py`):**
    *   Serves as the entry point and user interface.
    *   Parses command-line arguments (e.g., verbosity).
    *   Manages the main interaction loop, taking user input and displaying results.
    *   Initializes and orchestrates the CrewAI crew.
    *   Handles global state like the current working directory via the `StateManager`.
    *   Loads configuration from `.env` files.

2.  **Agent System (`claude_code/agents/`):**
    *   Powered by CrewAI, it consists of specialized agents, each with a defined role, goal, backstory, and a set of tools.
    *   A `TerminalCommander` agent acts as the orchestrator, delegating tasks to other specialist agents.

3.  **Tools (`claude_code/tools/`):**
    *   A collection of custom and wrapped CrewAI tools that agents use to perform actions.
    *   These include tools for safe shell command execution, file system operations, and web searching.
    *   Emphasis is placed on safety, with restrictions and validations built into the tools.

4.  **LLM Integration (`claude_code/utils/gemini_integration.py`, `claude_terminal.py`):**
    *   Abstracts the interaction with various Language Models (LLMs).
    *   Supports multiple LLM providers (Gemini, OpenAI, Anthropic, Ollama) through `langchain` wrappers.
    *   Configuration is managed via environment variables.

5.  **Utilities (`claude_code/utils/`):**
    *   `StateManager`: Manages persistent session state, such as the current working directory and command history, saving it to a JSON file.
    *   `gemini_integration`: Provides specific setup for Google Gemini LLMs.

### Interaction Flow

1.  User enters a command in the terminal.
2.  `claude_terminal.py` captures the input.
3.  A `Task` is created and assigned to the `TerminalCommander` agent.
4.  The `TerminalCommander` analyzes the task and may delegate sub-tasks to specialized agents (FileNavigator, CodeExecutor, WebResearcher).
5.  Specialized agents use their assigned tools to perform actions (e.g., list files, run a script, search the web).
6.  Results from the tools and agents are passed back to the `TerminalCommander`.
7.  The `TerminalCommander` synthesizes the information and formulates a final response.
8.  The response is displayed to the user. If the command involved a directory change (e.g., `cd`), the `StateManager` updates the CWD.

## Agent System

The assistant employs a multi-agent system using CrewAI. Each agent is designed for a specific set of tasks:

1.  **`TerminalCommander` (`claude_code.agents.create_terminal_commander`):**
    *   **Role:** Central orchestrator and interpreter of user commands.
    *   **Goal:** Understand user intent, delegate tasks to appropriate specialist agents, and consolidate their outputs into a coherent response.
    *   **Backstory:** Acts as an AI coding assistant in the terminal, cautious and safety-oriented.
    *   **Delegation:** Allowed.

2.  **`FileNavigator` (`claude_code.agents.create_file_navigator`):**
    *   **Role:** File System Expert.
    *   **Goal:** Navigate the file system, list directory contents, read files, and provide information about file structure.
    *   **Tools:**
        *   `SafeDirectoryTool`: For listing directory contents.
        *   `SafeFileReadTool`: For reading file contents.
        *   `SafeShellTool`: Limited to file system inspection commands (e.g., `ls`, `pwd`, `find`).
    *   **Delegation:** Not allowed.

3.  **`CodeExecutor` (`claude_code.agents.create_code_executor`):**
    *   **Role:** Secure Code Execution Specialist.
    *   **Goal:** Execute provided code snippets or shell commands in a controlled manner and return their output.
    *   **Tools:**
        *   `SafeShellTool`: Configured with a specific list of allowed execution-related commands (e.g., `python`, `pip`, `node`, `echo`).
    *   **Delegation:** Not allowed.

4.  **`WebResearcher` (`claude_code.agents.create_web_researcher`):**
    *   **Role:** Internet Research Analyst.
    *   **Goal:** Find information on the internet using search engines and by fetching content from specific URLs.
    *   **Tools:**
        *   `SerpAPITool`: For performing web searches via Serper API.
        *   `WebsiteTool`: For fetching and searching content from specific web pages.
    *   **Delegation:** Not allowed.

## LLM Integration

The assistant leverages Large Language Models (LLMs) for understanding natural language, planning, and generating responses.

*   **Provider Support:** Integration is primarily through a custom LangChain wrapper (`CustomGeminiLLM`) for the `google-generativeai` SDK, specifically for Google Gemini models.
    *   **Google Gemini:** Default and primary provider, configured via `CustomGeminiLLM` using `GEMINI_API_KEY` and `MODEL` from the `.env` file.
*   **Configuration:** The active LLM model and API key are specified in the `.env` file (`MODEL`, `GEMINI_API_KEY`).
*   **CrewAI Integration:** The `CustomGeminiLLM` instance is passed to the CrewAI `Agent` and `Crew` (for the manager LLM).
*   **Error Handling:** The `CustomGeminiLLM` includes checks for the API key and necessary packages.

### Acquiring `GOOGLE_APPLICATION_CREDENTIALS` (for ADC)

While the current `CustomGeminiLLM` uses a `GEMINI_API_KEY` directly, you might want to use Application Default Credentials (ADC) for other Google Cloud services or if you switch to an LLM configuration that leverages ADC (e.g., Vertex AI). Here's how to set up `GOOGLE_APPLICATION_CREDENTIALS`:

1.  **Navigate to Google Cloud Console:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Select your project or create a new one.

2.  **Enable Necessary APIs:**
    *   Ensure the APIs for the services you intend to use are enabled. For example, if you were to use Vertex AI, you would need the "Vertex AI API" enabled. Go to "APIs & Services" > "Library" to search and enable APIs.

3.  **Create a Service Account:**
    *   Go to "IAM & Admin" > "Service Accounts".
    *   Click on "+ CREATE SERVICE ACCOUNT".
    *   Fill in the service account details:
        *   **Service account name:** (e.g., `codex-simulator-sa`)
        *   **Service account ID:** (auto-generated or customize)
        *   **Description:** (e.g., "Service account for Codex Simulator application")
    *   Click "CREATE AND CONTINUE".

4.  **Grant Roles to the Service Account:**
    *   Assign appropriate roles to the service account based on the Google Cloud services it needs to access. For example:
        *   If using Vertex AI: Assign the "Vertex AI User" role.
        *   If accessing Google Drive: Assign relevant Drive API scopes/roles.
        *   Choose roles that grant the minimum necessary permissions.
    *   Click "CONTINUE".

5.  **Create a Key for the Service Account:**
    *   Skip "Grant users access to this service account" for now (unless needed). Click "DONE".
    *   Find your newly created service account in the list.
    *   Click on the three dots (Actions) next to it and select "Manage keys".
    *   Click on "ADD KEY" > "Create new key".
    *   Choose **JSON** as the key type and click "CREATE".
    *   A JSON file containing your service account key will be downloaded to your computer. **Keep this file secure, as it grants access to your Google Cloud resources.**

6.  **Set the Environment Variable:**
    *   Move the downloaded JSON key file to a secure, persistent location on your system (e.g., within your project directory if it's gitignored, or a dedicated credentials directory).
    *   Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the absolute path of this JSON key file. You've already added this to your `.env` file:
        ```
        GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/downloaded-key-file.json
        ```
        Ensure the path in your `.env` file (`/Users/sinmi/Documents/DREAMGANG/ted_talk_content_generator_systems_thinking/youtube_content_creator/GoogleCloud/youtube_content_service_accounts.json`) is correct and points to the downloaded JSON key.

    *   The `python-dotenv` library will load this variable from your `.env` file when the application starts.

**Important Note:** The `CustomGeminiLLM` as currently implemented in this project uses the `GEMINI_API_KEY` for authentication with the `google-generativeai` SDK. The `GOOGLE_APPLICATION_CREDENTIALS` setup is for authenticating with Google Cloud services that support ADC, which might include different LLM access methods (like Vertex AI SDKs) or other Google Cloud APIs. If you intend for `CustomGeminiLLM` to use ADC, its implementation would need to be changed to use a library or authentication flow that respects `GOOGLE_APPLICATION_CREDENTIALS` (e.g., using the `google-auth` library to get credentials for Vertex AI).

## Tools

The assistant's agents are equipped with a suite of tools, many of which are safety-enhanced versions of standard `crewai-tools`.

1.  **`SafeShellTool` (`claude_code.tools.SafeShellTool`):**
    *   Allows execution of shell commands.
    *   **Safety:** Enforces a configurable whitelist of allowed commands (e.g., `ls`, `python`) and a blacklist of explicitly blocked commands or command patterns (e.g., `rm`, `sudo`, output redirection). This is crucial for preventing accidental or malicious system operations.
    *   Used by `FileNavigator` (with a restricted set of commands) and `CodeExecutor`.

2.  **`SafeDirectoryTool` (`claude_code.tools.SafeDirectoryTool`):**
    *   Based on `crewai_tools.DirectoryReadTool`.
    *   **Safety:** Validates directory paths, restricting access to sensitive system directories (e.g., `/etc`, `/root`).
    *   Used by `FileNavigator`.

3.  **`SafeFileReadTool` (`claude_code.tools.SafeFileReadTool`):**
    *   Based on `crewai_tools.FileReadTool`.
    *   **Safety:** Validates file paths, restricting access to known sensitive files (e.g., `/etc/passwd`, `.env`) and directories. It also imposes a file size limit (1MB) to prevent performance issues with very large files.
    *   Used by `FileNavigator`.

4.  **`SerpAPITool` (`claude_code.tools.SerpAPITool`):**
    *   A wrapper around `crewai_tools.SerperDevTool`.
    *   Provides web search capabilities using the Serper API (`SERPER_API_KEY`).
    *   Used by `WebResearcher`.

5.  **`WebsiteTool` (`claude_code.tools.WebsiteTool`):**
    *   A tool to fetch and summarize content from specific URLs using `requests` and `BeautifulSoup`.
    *   It does not require any external API keys for its core functionality.
    *   Used by `WebResearcher`.

## Safety Measures

Security and safety are key considerations in the design of the Claude Code Terminal Assistant, especially given its ability to interact with the file system and execute commands.

1.  **Restricted Shell Commands (`SafeShellTool`):**
    *   The `SafeShellTool` is the primary mechanism for executing shell commands.
    *   It operates with a configurable list of allowed commands and blocks potentially dangerous commands (e.g., `rm`, `sudo`, `mkfs`) and patterns (e.g., output redirection `>` and `|`, `eval`, `exec`).
    *   Different agents (like `FileNavigator` and `CodeExecutor`) can be instantiated with different sets of allowed commands appropriate for their roles.

2.  **Path Validation (`SafeDirectoryTool`, `SafeFileReadTool`):**
    *   Tools interacting with the file system perform path validation.
    *   Access to sensitive system directories (e.g., `/etc`, `/var`, `/root`) and specific sensitive files (e.g., `/etc/passwd`, `.ssh/id_rsa`) is blocked.

3.  **File Size Limits (`SafeFileReadTool`):**
    *   `SafeFileReadTool` imposes a limit on the size of files that can be read (currently 1MB) to prevent accidental reading of very large files that could impact performance or lead to excessive output.

4.  **Agent Specialization and Limited Delegation:**
    *   Specialist agents (`FileNavigator`, `CodeExecutor`, `WebResearcher`) have focused roles and do not delegate further, reducing the potential attack surface.
    *   The `TerminalCommander` is responsible for delegation but is designed with a cautious backstory.

5.  **User Acknowledgment:**
    *   A safety warning is displayed to the user upon starting the assistant (unless disabled with `--no-warning`), informing them of the assistant's capabilities and potential risks.

6.  **No Direct File Modification Tools:**
    *   Currently, there are no tools that directly write to or modify files. File operations are read-only or involve execution that might create files (e.g., a Python script writing output).

7.  **Environment Variable Management:**
    *   API keys and sensitive configurations are managed through `.env` files and environment variables, not hardcoded.

While these measures enhance safety, users should always exercise caution, especially when asking the assistant to execute commands or scripts.


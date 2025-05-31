CLAUDE CODE
Claude Code overview

Copy page

Learn about Claude Code, an agentic coding tool made by Anthropic.
Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. By integrating directly with your development environment, Claude Code streamlines your workflow without requiring additional servers or complex setup.

Copy
npm install -g @anthropic-ai/claude-code
Claude Code’s key capabilities include:
* 		Editing files and fixing bugs across your codebase
* 		Answering questions about your code’s architecture and logic
* 		Executing and fixing tests, linting, and other commands
* 		Searching through git history, resolving merge conflicts, and creating commits and PRs
* 		Browsing documentation and resources from the internet using web search
* 		Works with Amazon Bedrock and Google Vertex AI for enterprise deployments
​

Why Claude Code?
Claude Code operates directly in your terminal, understanding your project context and taking real actions. No need to manually add files to context - Claude will explore your codebase as needed.
​

Enterprise integration
Claude Code seamlessly integrates with enterprise AI platforms. You can connect to Amazon Bedrock or Google Vertex AI for secure, compliant deployments that meet your organization’s requirements.
​

Security and privacy by design
Your code’s security is paramount. Claude Code’s architecture ensures:
* 		Direct API connection: Your queries go straight to Anthropic’s API without intermediate servers
* 		Works where you work: Operates directly in your terminal
* 		Understands context: Maintains awareness of your entire project structure
* 		Takes action: Performs real operations like editing files and creating commits
​

Getting started
To get started with Claude Code, follow our installation guide which covers system requirements, installation steps, and authentication process.
​

Quick tour
Here’s what you can accomplish with Claude Code:
​

From questions to solutions in seconds

Copy
# Ask questions about your codebase
claude
> how does our authentication system work?

# Create a commit with one command
claude commit

# Fix issues across multiple files
claude "fix the type errors in the auth module"
​

Understand unfamiliar code

Copy
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
​

Automate Git operations

Copy
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
​
CLAUDE CODE
Getting started with Claude Code

Copy page

Learn how to install, authenticate, and start using Claude Code.
​

Check system requirements
* 		Operating Systems: macOS 10.15+, Ubuntu 20.04+/Debian 10+, or Windows via WSL
* 		Hardware: 4GB RAM minimum
* 		Software:
    * 		Node.js 18+
    * 		git 2.23+ (optional)
    * 		GitHub or GitLab CLI for PR workflows (optional)
    * 		ripgrep (rg) for enhanced file search (optional)
* 		Network: Internet connection required for authentication and AI processing
* 		Location: Available only in supported countries

Troubleshooting WSL installation
Currently, Claude Code does not run directly in Windows, and instead requires WSL. If you encounter issues in WSL:
1. OS/platform detection issues: If you receive an error during installation, WSL may be using Windows npm. Try:
    * 		Run npm config set os linux before installation
    * 		Install with npm install -g @anthropic-ai/claude-code --force --no-os-check (Do NOT use sudo)
2. Node not found errors: If you see exec: node: not found when running claude, your WSL environment may be using a Windows installation of Node.js. You can confirm this with which npm and which node, which should point to Linux paths starting with /usr/ rather than /mnt/c/. To fix this, try installing Node via your Linux distribution’s package manager or via nvm.
​

Install and authenticate

1
Install Claude Code
Install NodeJS 18+, then run:

Copy
npm install -g @anthropic-ai/claude-code

Do NOT use sudo npm install -g as this can lead to permission issues and security risks. If you encounter permission errors, see configure Claude Code for recommended solutions.

2
Navigate to your project

Copy
cd your-project-directory 

3
Start Claude Code

Copy
claude

4
Complete authentication
Claude Code offers multiple authentication options:
1. Anthropic Console: The default option. Connect through the Anthropic Console and complete the OAuth process. Requires active billing at console.anthropic.com.
2. Claude App (with Max plan): Subscribe to Claude’s Max plan for a single subscription that includes both Claude Code and the web interface. Get more value at the same price point while managing your account in one place. Log in with your Claude.ai account. During launch, choose the option that matches your subscription type.
3. Enterprise platforms: Configure Claude Code to use Amazon Bedrock or Google Vertex AI for enterprise deployments with your existing cloud infrastructure.
​

Initialize your project
For first-time users, we recommend:

1
Start Claude Code

Copy
claude

2
Run a simple command

Copy
summarize this project

3
Generate a CLAUDE.md project guide

Copy
/init 

4
Commit the generated CLAUDE.md file
Ask Claude to commit the generated CLAUDE.md file to your repository.
Was this page helpful?

Yes

No

Overview
Common tasks

x

linkedin


On this page
* 		Check system requirements
* 		Install and authenticate
* 		Initialize your project
Getting started with Claude Code - AnthropicCLAUDE CODE
Core tasks and workflows

Copy page

Explore Claude Code’s powerful features for editing, searching, testing, and automating your development workflow.
Claude Code operates directly in your terminal, understanding your project context and taking real actions. No need to manually add files to context - Claude will explore your codebase as needed.
​

Understand unfamiliar code

Copy
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works
​

Automate Git operations

Copy
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts
​

Edit code intelligently

Copy
> add input validation to the signup form
> refactor the logger to use the new API
> fix the race condition in the worker queue
​

Test and debug your code

Copy
> run tests for the auth module and fix failures
> find and fix security vulnerabilities
> explain why this test is failing
​

Encourage deeper thinking
For complex problems, explicitly ask Claude to think more deeply:

Copy
> think about how we should architect the new payment service
> think hard about the edge cases in our authentication flow
Claude Code will show when the model is using extended thinking. You can proactively prompt Claude to “think” or “think deeply” for more planning-intensive tasks. We suggest that you first tell Claude about your task and let it gather context from your project. Then, ask it to “think” to create a plan.

Claude will think more based on the words you use. For example, “think hard” will trigger more extended thinking than saying “think” alone.
For more tips, see Extended thinking tips.
​

Automate CI and infra workflows
Claude Code comes with a non-interactive mode for headless execution. This is especially useful for running Claude Code in non-interactive contexts like scripts, pipelines, and Github Actions.
Use --print (-p) to run Claude in non-interactive mode. In this mode, you can set the ANTHROPIC_API_KEY environment variable to provide a custom API key.
Non-interactive mode is especially useful when you pre-configure the set of commands Claude is allowed to use:

Copy
export ANTHROPIC_API_KEY=sk_...
claude -p "update the README with the latest changes" --allowedTools "Bash(git diff:*)" "Bash(git log:*)" Write --disallowedTools ...CLAUDE CODE
CLI usage and controls

Copy page

Learn how to use Claude Code from the command line, including CLI commands, flags, and slash commands.
​

Getting started
Claude Code provides two main ways to interact:
* 		Interactive mode: Run claude to start a REPL session
* 		One-shot mode: Use claude -p "query" for quick commands

Copy
# Start interactive mode
claude

# Start with an initial query
claude "explain this project"

# Run a single command and exit
claude -p "what does this function do?"

# Process piped content
cat logs.txt | claude -p "analyze these errors"
​

CLI commands
Command	Description	Example
claude	Start interactive REPL	claude
claude "query"	Start REPL with initial prompt	claude "explain this project"
claude -p "query"	Run one-off query, then exit	claude -p "explain this function"
cat file | claude -p "query"	Process piped content	cat logs.txt | claude -p "explain"
claude -c	Continue most recent conversation	claude -c
claude -c -p "query"	Continue in print mode	claude -c -p "Check for type errors"
claude -r "<session-id>" "query"	Resume session by ID	claude -r "abc123" "Finish this PR"
claude config	Configure settings	claude config set --global theme dark
claude update	Update to latest version	claude update
claude mcp	Configure Model Context Protocol servers	See MCP section in tutorials
​

CLI flags
Customize Claude Code’s behavior with these command-line flags:
Flag	Description	Example
--allowedTools	A list of tools that should be allowed without prompting the user for permission, in addition to settings.json files	"Bash(git log:*)" "Bash(git diff:*)" "Write"
--disallowedTools	A list of tools that should be disallowed without prompting the user for permission, in addition to settings.json files	"Bash(git log:*)" "Bash(git diff:*)" "Write"
--print, -p	Print response without interactive mode (see SDK documentation for programmatic usage details)	claude -p "query"
--output-format	Specify output format for print mode (options: text, json, stream-json)	claude -p "query" --output-format json
--verbose	Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes)	claude --verbose
--max-turns	Limit the number of agentic turns in non-interactive mode	claude -p --max-turns 3 "query"
--model	Sets the model for the current session with an alias for the latest model (sonnet or opus) or a model’s full name	claude --model claude-sonnet-4-20250514
--permission-prompt-tool	Specify an MCP tool to handle permission prompts in non-interactive mode	claude -p --permission-prompt-tool mcp_auth_tool "query"
--resume	Resume a specific session by ID, or by choosing in interactive mode	claude --resume abc123 "query"
--continue	Load the most recent conversation in the current directory	claude --continue
--dangerously-skip-permissions	Skip permission prompts (use with caution)	claude --dangerously-skip-permissions
The --output-format json flag is particularly useful for scripting and automation, allowing you to parse Claude’s responses programmatically.
For detailed information about print mode (-p) including output formats, streaming, verbose logging, and programmatic usage, see the SDK documentation.
​

Slash commands
Control Claude’s behavior during an interactive session:
Command	Purpose	
/bug	Report bugs (sends conversation to Anthropic)	
/clear	Clear conversation history	
/compact [instructions]	Compact conversation with optional focus instructions	
/config	View/modify configuration	
/cost	Show token usage statistics	
/doctor	Checks the health of your Claude Code installation	
/help	Get usage help	
/init	Initialize project with CLAUDE.md guide	
/login	Switch Anthropic accounts	
/logout	Sign out from your Anthropic account	
/memory	Edit CLAUDE.md memory files	
/model	Select or change the AI model	
/pr_comments	View pull request comments	
/review	Request code review	
/status	View account and system statuses	
/terminal-setup	Install Shift+Enter key binding for newlines (iTerm2 and VSCode only)	
/vim	Enter vim mode for alternating insert and command modes	
​

Special shortcuts
​

Quick memory with #
Add memories instantly by starting your input with #:

Copy
# Always use descriptive variable names
You’ll be prompted to select which memory file to store this in.
​

Line breaks in terminal
Enter multiline commands using:
* 		Quick escape: Type \ followed by Enter
* 		Keyboard shortcut: Option+Enter (or Shift+Enter if configured)
To set up Option+Enter in your terminal:
For Mac Terminal.app:
1. Open Settings → Profiles → Keyboard
2. Check “Use Option as Meta Key”
For iTerm2 and VSCode terminal:
1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to “Esc+”
Tip for iTerm2 and VSCode users: Run /terminal-setup within Claude Code to automatically configure Shift+Enter as a more intuitive alternative.
See terminal setup in settings for configuration details.
​

Vim Mode
Claude Code supports a subset of Vim keybindings that can be enabled with /vim or configured via /config.
The supported subset includes:
* 		Mode switching: Esc (to NORMAL), i/I, a/A, o/O (to INSERT)
* 		Navigation: h/j/k/l, w/e/b, 0/$/^, gg/G
* 		Editing: x, dw/de/db/dd/D, cw/ce/cb/cc/C, . (repeat)CLAUDE CODE
* IDE integrations
* 
* Copy page
* 
* Integrate Claude Code with your favorite development environments
* Claude Code seamlessly integrates with popular Integrated Development Environments (IDEs) to enhance your coding workflow. This integration allows you to leverage Claude’s capabilities directly within your preferred development environment.
* ​
* 
* Supported IDEs
* Claude Code currently supports two major IDE families:
* 		Visual Studio Code (including popular forks like Cursor and Windsurf)
* 		JetBrains IDEs (including PyCharm, WebStorm, IntelliJ, and GoLand)
* ​
* 
* Features
* 		Quick launch: Use Cmd+Esc (Mac) or Ctrl+Esc (Windows/Linux) to open Claude Code directly from your editor, or click the Claude Code button in the UI
* 		Diff viewing: Code changes can be displayed directly in the IDE diff viewer instead of the terminal. You can configure this in /config
* 		Selection context: The current selection/tab in the IDE is automatically shared with Claude Code
* 		File reference shortcuts: Use Cmd+Option+K (Mac) or Alt+Ctrl+K (Linux/Windows) to insert file references (e.g., @File#L1-99)
* 		Diagnostic sharing: Diagnostic errors (lint, syntax, etc.) from the IDE are automatically shared with Claude as you work
* ​
* 
* Installation
* ​
* 
* VS Code
* Open VSCode
* Open the integrated terminal
* Run claude - the extension will auto-install
* Going forward you can also use the /ide command in any external terminal to connect to the IDE.
* 
* These installation instructions also apply to VS Code forks like Cursor and Windsurf.
* ​
* 
* JetBrains IDEs
* Install the Claude Code plugin from the marketplace and restart your IDE.
* 
* The plugin may also be auto-installed when you run claude in the integrated terminal. The IDE must be restarted completely to take effect.
* 
* Remote Development Limitations: When using JetBrains Remote Development, you must install the plugin in the remote host via Settings > Plugin (Host).
* ​
* 
* Configuration
* Both integrations work with Claude Code’s configuration system. To enable IDE-specific features:
* Connect Claude Code to your IDE by running claude in the built-in terminal
* Run the /config command
* Set the diff tool to auto for automatic IDE detection
* Claude Code will automatically use the appropriate viewer based on your IDE
* If you’re using an external terminal (not the IDE’s built-in terminal), you can still connect to your IDE by using the /ide command after launching Claude Code. This allows you to benefit from IDE integration features even when running Claude from a separate terminal application. This works for both VS Code and JetBrains IDEs.
* 
* When using an external terminal, to ensure Claude has default access to the same files as your IDE, start Claude from the same directory as your IDE project root.
* ​
* 
* Troubleshooting
* ​
* 
* VS Code extension not installing
* 		Ensure you’re running Claude Code from VS Code’s integrated terminal
* 		Ensure that the CLI corresponding to your IDE is installed:
    * 		For VS Code: code command should be available
    * 		For Cursor: cursor command should be available
    * 		For Windsurf: windsurf command should be available
    * 		If not installed, use Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux) and search for “Shell Command: Install ‘code’ command in PATH” (or the equivalent for your IDE)
* 		Check that VS Code has permission to install extensions
* ​
* 
* JetBrains plugin not working
* 		Ensure you’re running Claude Code from the project root directory
* 		Check that the JetBrains plugin is enabled in the IDE settings
* 		Completely restart the IDE. You may need to do this multiple times
* 		For JetBrains Remote Development, ensure that the Claude Code plugin is installed in the remote host and not locally on the client
* For additional help, refer to our troubleshooting guide or reach out to support.
* Was this page helpful?
* 
* Yes

CLAUDE CODE
Manage Claude's memory

Copy page

Learn how to manage Claude Code’s memory across sessions with different memory locations and best practices.
Claude Code can remember your preferences across sessions, like style guidelines and common commands in your workflow.
​

Determine memory type
Claude Code offers three memory locations, each serving a different purpose:
Memory Type	Location	Purpose	Use Case Examples
Project memory	./CLAUDE.md	Team-shared instructions for the project	Project architecture, coding standards, common workflows
User memory	~/.claude/CLAUDE.md	Personal preferences for all projects	Code styling preferences, personal tooling shortcuts
Project memory (local)	./CLAUDE.local.md	Personal project-specific preferences	(Deprecated, see below) Your sandbox URLs, preferred test data
All memory files are automatically loaded into Claude Code’s context when launched.
​

CLAUDE.md imports
CLAUDE.md files can import additional files using @path/to/import syntax. The following example imports 3 files:

Copy
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
Both relative and absolute paths are allowed. In particular, importing files in user’s home dir is a convenient way for your team members to provide individual instructions that are not checked into the repository. Previously CLAUDE.local.md served a similar purpose, but is now deprecated in favor of imports since they work better across multiple git worktrees.

Copy
# Individual Preferences
- @~/.claude/my-project-instructions.md
To avoid potential collisions, imports are not evaluated inside markdown code spans and code blocks.

Copy
This code span will not be treated as an import: `@anthropic-ai/claude-code`
Imported files can recursively import additional files, with a max-depth of 5 hops. You can see what memory files are loaded by running /memory command.
​

How Claude looks up memories
Claude Code reads memories recursively: starting in the cwd, Claude Code recurses up to / and reads any CLAUDE.md or CLAUDE.local.md files it finds. This is especially convenient when working in large repositories where you run Claude Code in foo/bar/, and have memories in both foo/CLAUDE.md and foo/bar/CLAUDE.md.
Claude will also discover CLAUDE.md nested in subtrees under your current working directory. Instead of loading them at launch, they are only included when Claude reads files in those subtrees.
​

Quickly add memories with the # shortcut
The fastest way to add a memory is to start your input with the # character:

Copy
# Always use descriptive variable names
You’ll be prompted to select which memory file to store this in.
​

Directly edit memories with /memory
Use the /memory slash command during a session to open any memory file in your system editor for more extensive additions or organization.
​

Memory best practices
* 		Be specific: “Use 2-space indentation” is better than “Format code properly”.
* 		Use structure to organize: Format each individual memory as a bullet point and group related memories under descriptive markdown headings.
		Review periodically: Update memories as your project evolves to ensure Claude is always using the most up to date information and context.CLAUDE CODE
Claude Code settings

Copy page

Learn how to configure Claude Code with global and project-level settings, themes, and environment variables.
Claude Code offers a variety of settings to configure its behavior to meet your needs. You can configure Claude Code by running claude config in your terminal, or the /config command when using the interactive REPL.
​

Configuration hierarchy
The new settings.json file is our official mechanism for configuring Claude Code through hierarchical settings:
* 		User settings are defined in ~/.claude/settings.json and apply to all projects.
* 		Project settings are saved in your project directory under .claude/settings.json for shared settings, and .claude/settings.local.json for local project settings. Claude Code will configure git to ignore .claude/settings.local.json when it is created.
* 		For enterprise deployments of Claude Code, we also support enterprise managed policy settings. These take precedence over user and project settings. System administrators can deploy policies to /Library/Application Support/ClaudeCode/policies.json on macOS and /etc/claude-code/policies.json on Linux and Windows via WSL.
Example settings.json

Copy
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
​

Available settings
settings.json supports a number of options:
Key	Description	Example
apiKeyHelper	Custom script to generate an Anthropic API key	/bin/generate_temp_api_key.sh
cleanupPeriodDays	How long to locally retain chat transcripts (default: 30 days)	20
env	Environment variables that will be applied to every session	{"FOO": "bar"}
includeCoAuthoredBy	Whether to include the co-authored-by Claude byline in git commits and pull requests (default: true)	false
​

Settings precedence
Settings are applied in order of precedence:
1. Enterprise policies
2. Command line arguments
3. Local project settings
4. Shared project settings
5. User settings
​

Configuration options
Claude Code supports global and project-level configuration.
To manage your configurations, use the following commands:
* 		List settings: claude config list
* 		See a setting: claude config get <key>
* 		Change a setting: claude config set <key> <value>
* 		Push to a setting (for lists): claude config add <key> <value>
* 		Remove from a setting (for lists): claude config remove <key> <value>
By default config changes your project configuration. To manage your global configuration, use the --global (or -g) flag.
​

Global configuration
To set a global configuration, use claude config set -g <key> <value>:
Key	Description	Example
autoUpdaterStatus	Enable or disable the auto-updater (default: enabled)	disabled
preferredNotifChannel	Where you want to receive notifications (default: iterm2)	iterm2, iterm2_with_bell, terminal_bell, or notifications_disabled
theme	Color theme	dark, light, light-daltonized, or dark-daltonized
verbose	Whether to show full bash and command outputs (default: false)	true
We are in the process of migration global configuration to settings.json.
​

Permissions
You can manage Claude Code’s tool permissions with /allowed-tools. This UI lists all permission rules and the settings.json file they are sourced from.
* 		Allow rules will allow Claude Code to use the specified tool without further manual approval.
* 		Deny rules will prevent Claude Code from using the specified tool. Deny rules take precedence over allow rules.
Permission rules use the format: Tool(optional-specifier).
For example, adding WebFetch to the list of allow rules would allow any use of the web fetch tool without requiring user approval. See the list of tools available to Claude (use the name in parentheses when provided.)
Some tools use the optional specifier for more fine-grained permission controls. For example, an allow rule with WebFetch(domain:example.com) would allow fetches to example.com but not other URLs.
Bash rules can be exact matches like Bash(npm run build), or prefix matches when they end with :* like Bash(npm run test:*)
Read() and Edit() rules follow the gitignore specification. Patterns are resolved relative to the directory containing .claude/settings.json. To reference an absolute path, use //. For a path relative to your home directory, use ~/. For example Read(//tmp/build_cache) or Edit(~/.zshrc). Claude will also make a best-effort attempt to apply Read and Edit rules to other file-related tools like Grep, Glob, and LS.
MCP tool names follow the format: mcp__server_name__tool_name where:
* 		server_name is the name of the MCP server as configured in Claude Code
* 		tool_name is the specific tool provided by that server
More examples:
Rule	Description	
Bash(npm run build)	Matches the exact Bash command npm run build.	
Bash(npm run test:*)	Matches Bash commands starting with npm run test. See note below about command separator handling.	
Edit(~/.zshrc)	Matches the ~/.zshrc file.	
Read(node_modules/**)	Matches any node_modules directory.	
mcp__puppeteer__puppeteer_navigate	Matches the puppeteer_navigate tool from the puppeteer MCP server.	
WebFetch(domain:example.com)	Matches fetch requests to example.com	
Claude Code is aware of command separators (like &&) so a prefix match rule like Bash(safe-cmd:*) won’t give it permission to run the command safe-cmd && other-cmd
​

Auto-updater permission options
When Claude Code detects that it doesn’t have sufficient permissions to write to your global npm prefix directory (required for automatic updates), you’ll see a warning that points to this documentation page. For detailed solutions to auto-updater issues, see the troubleshooting guide.
​

Recommended: Create a new user-writable npm prefix

Copy
# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/npm-global-packages.txt and install packages you want to keep
# npm install -g package1 package2 package3...
Why we recommend this option:
* 		Avoids modifying system directory permissions
* 		Creates a clean, dedicated location for your global npm packages
* 		Follows security best practices
Since Claude Code is actively developing, we recommend setting up auto-updates using the recommended option above.
​

Disabling the auto-updater
If you prefer to disable the auto-updater instead of fixing permissions, you can use:

Copy
claude config set -g autoUpdaterStatus disabled
​

Optimize your terminal setup
Claude Code works best when your terminal is properly configured. Follow these guidelines to optimize your experience.
Supported shells:
* 		Bash
* 		Zsh
* 		Fish
​

Themes and appearance
Claude cannot control the theme of your terminal. That’s handled by your terminal application. You can match Claude Code’s theme to your terminal during onboarding or any time via the /config command
​

Line breaks
You have several options for entering linebreaks into Claude Code:
* 		Quick escape: Type \ followed by Enter to create a newline
* 		Keyboard shortcut: Press Option+Enter (Meta+Enter) with proper configuration
To set up Option+Enter in your terminal:
For Mac Terminal.app:
1. Open Settings → Profiles → Keyboard
2. Check “Use Option as Meta Key”
For iTerm2 and VSCode terminal:
1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to “Esc+”
Tip for iTerm2 and VSCode users: Run /terminal-setup within Claude Code to automatically configure Shift+Enter as a more intuitive alternative.
​

Notification setup
Never miss when Claude completes a task with proper notification configuration:
​

Terminal bell notifications
Enable sound alerts when tasks complete:

Copy
claude config set --global preferredNotifChannel terminal_bell
For macOS users: Don’t forget to enable notification permissions in System Settings → Notifications → [Your Terminal App].
​

iTerm 2 system notifications
For iTerm 2 alerts when tasks complete:
1. Open iTerm 2 Preferences
2. Navigate to Profiles → Terminal
3. Enable “Silence bell” and Filter Alerts → “Send escape sequence-generated alerts”
4. Set your preferred notification delay
Note that these notifications are specific to iTerm 2 and not available in the default macOS Terminal.
​

Handling large inputs
When working with extensive code or long instructions:
* 		Avoid direct pasting: Claude Code may struggle with very long pasted content
* 		Use file-based workflows: Write content to a file and ask Claude to read it
* 		Be aware of VS Code limitations: The VS Code terminal is particularly prone to truncating long pastes
​

Vim Mode
Claude Code supports a subset of Vim keybindings that can be enabled with /vim or configured via /config.
The supported subset includes:
* 		Mode switching: Esc (to NORMAL), i/I, a/A, o/O (to INSERT)
* 		Navigation: h/j/k/l, w/e/b, 0/$/^, gg/G
* 		Editing: x, dw/de/db/dd/D, cw/ce/cb/cc/C, . (repeat)
​

Environment variables
Claude Code supports the following environment variables to control its behavior:

All environment variables can also be configured in settings.json. This is useful as a way to automatically set environment variables for each session, or to roll out a set of environment variables for your whole team or organization.
Variable	Purpose	
ANTHROPIC_API_KEY	API key, only when using the Claude SDK (for interactive usage, run /login)	
ANTHROPIC_AUTH_TOKEN	Custom value for the Authorization and Proxy-Authorization headers (the value you set here will be prefixed with Bearer )	
ANTHROPIC_CUSTOM_HEADERS	Custom headers you want to add to the request (in Name: Value format)	
ANTHROPIC_MODEL	Name of custom model to use (see Model Configuration)	
ANTHROPIC_SMALL_FAST_MODEL	Name of Haiku-class model for background tasks	
BASH_DEFAULT_TIMEOUT_MS	Default timeout for long-running bash commands	
BASH_MAX_TIMEOUT_MS	Maximum timeout the model can set for long-running bash commands	
BASH_MAX_OUTPUT_LENGTH	Maximum number of characters in bash outputs before they are middle-truncated	
CLAUDE_CODE_API_KEY_HELPER_TTL_MS	Interval at which credentials should be refreshed (when using apiKeyHelper)	
CLAUDE_CODE_USE_BEDROCK	Use Bedrock (see Bedrock & Vertex)	
CLAUDE_CODE_USE_VERTEX	Use Vertex (see Bedrock & Vertex)	
CLAUDE_CODE_SKIP_VERTEX_AUTH	Skip Google authentication for Vertex (eg. when using a proxy)	
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC	Equivalent of setting DISABLE_AUTOUPDATER, DISABLE_BUG_COMMAND, DISABLE_ERROR_REPORTING, and DISABLE_TELEMETRY	
DISABLE_AUTOUPDATER	Set to 1 to disable the automatic updater	
DISABLE_BUG_COMMAND	Set to 1 to disable the /bug command	
DISABLE_COST_WARNINGS	Set to 1 to disable cost warning messages	
DISABLE_ERROR_REPORTING	Set to 1 to opt out of Sentry error reporting	
DISABLE_TELEMETRY	Set to 1 to opt out of Statsig telemetry (note that Statsig events do not include user data like code, file paths, or bash commands)	
HTTP_PROXY	Specify HTTP proxy server for network connections	
HTTPS_PROXY	Specify HTTPS proxy server for network connections	
MAX_THINKING_TOKENS	Force a thinking for the model budget	
MCP_TIMEOUT	Timeout in milliseconds for MCP server startup	
MCP_TOOL_TIMEOUT	Timeout in milliseconds for MCP tool execution	

CLAUDE CODE
Manage permissions and security

Copy page

Learn about Claude Code’s permission system, tools access, and security safeguards.
Claude Code uses a tiered permission system to balance power and safety:
Tool Type	Example	Approval Required	”Yes, don’t ask again” Behavior
Read-only	File reads, LS, Grep	No	N/A
Bash Commands	Shell execution	Yes	Permanently per project directory and command
File Modification	Edit/write files	Yes	Until session end
​

Tools available to Claude
Claude Code has access to a set of powerful tools that help it understand and modify your codebase:
Tool	Description	Permission Required	
Agent	Runs a sub-agent to handle complex, multi-step tasks	No	
Bash	Executes shell commands in your environment	Yes	
Edit	Makes targeted edits to specific files	Yes	
Glob	Finds files based on pattern matching	No	
Grep	Searches for patterns in file contents	No	
LS	Lists files and directories	No	
MultiEdit	Performs multiple edits on a single file atomically	Yes	
NotebookEdit	Modifies Jupyter notebook cells	Yes	
NotebookRead	Reads and displays Jupyter notebook contents	No	
Read	Reads the contents of files	No	
TodoRead	Reads the current session’s task list	No	
TodoWrite	Creates and manages structured task lists	No	
WebFetch	Fetches content from a specified URL	Yes	
WebSearch	Performs web searches with domain filtering	Yes	
Write	Creates or overwrites files	Yes	
Permission rules can be configured using /allowed-tools or in permission settings.
​

Protect against prompt injection
Prompt injection is a technique where an attacker attempts to override or manipulate an AI assistant’s instructions by inserting malicious text. Claude Code includes several safeguards against these attacks:
* 		Permission system: Sensitive operations require explicit approval
* 		Context-aware analysis: Detects potentially harmful instructions by analyzing the full request
* 		Input sanitization: Prevents command injection by processing user inputs
* 		Command blocklist: Blocks risky commands that fetch arbitrary content from the web like curl and wget
Best practices for working with untrusted content:
1. Review suggested commands before approval
2. Avoid piping untrusted content directly to Claude
3. Verify proposed changes to critical files
4. Report suspicious behavior with /bug

While these protections significantly reduce risk, no system is completely immune to all attacks. Always maintain good security practices when working with any AI tool.
​

Configure network access
Claude Code requires access to:
* 		api.anthropic.com
* 		statsig.anthropic.com
* 		sentry.io
Allowlist these URLs when using Claude Code in containerized environments.
​

Development container reference implementation
Claude Code provides a development container configuration for teams that need consistent, secure environments. This preconfigured devcontainer setup works seamlessly with VS Code’s Remote - Containers extension and similar tools.
The container’s enhanced security measures (isolation and firewall rules) allow you to run claude --dangerously-skip-permissions to bypass permission prompts for unattended operation. We’ve included a reference implementation that you can customize for your needs.

While the devcontainer provides substantial protections, no system is completely immune to all attacks. Always maintain good security practices and monitor Claude’s activities.
​

Key features
* 		Production-ready Node.js: Built on Node.js 20 with essential development dependencies
* 		Security by design: Custom firewall restricting network access to only necessary services
* 		Developer-friendly tools: Includes git, ZSH with productivity enhancements, fzf, and more
* 		Seamless VS Code integration: Pre-configured extensions and optimized settings
* 		Session persistence: Preserves command history and configurations between container restarts
* 		Works everywhere: Compatible with macOS, Windows, and Linux development environments
​

Getting started in 4 steps
1. Install VS Code and the Remote - Containers extension
2. Clone the Claude Code reference implementation repository
3. Open the repository in VS Code
4. When prompted, click “Reopen in Container” (or use Command Palette: Cmd+Shift+P → “Remote-Containers: Reopen in Container”)
​

Configuration breakdown
The devcontainer setup consists of three primary components:
* 		devcontainer.json: Controls container settings, extensions, and volume mounts
* 		Dockerfile: Defines the container image and installed tools
* 		init-firewall.sh: Establishes network security rules
​

Security features
The container implements a multi-layered security approach with its firewall configuration:
* 		Precise access control: Restricts outbound connections to whitelisted domains only (npm registry, GitHub, Anthropic API, etc.)
* 		Default-deny policy: Blocks all other external network access
* 		Startup verification: Validates firewall rules when the container initializes
* 		Isolation: Creates a secure development environment separated from your main system
​

Customization options
The devcontainer configuration is designed to be adaptable to your needs:
* 		Add or remove VS Code extensions based on your workflow
* 		Modify resource allocations for different hardware environments
* 		Adjust network access permissions
* 		Customize shell configurations and developer tooling
* CLAUDE CODE
* Troubleshooting
* 
* Copy page
* 
* Solutions for common issues with Claude Code installation and usage.
* ​
* 
* Common installation issues
* ​
* 
* Linux permission issues
* When installing Claude Code with npm, you may encounter permission errors if your npm global prefix is not user writable (eg. /usr, or /usr/local).
* ​
* 
* Recommended solution: Create a user-writable npm prefix
* The safest approach is to configure npm to use a directory within your home folder:
* 
* Copy
* # First, save a list of your existing global packages for later migration
* npm list -g --depth=0 > ~/npm-global-packages.txt
* 
* # Create a directory for your global packages
* mkdir -p ~/.npm-global
* 
* # Configure npm to use the new directory path
* npm config set prefix ~/.npm-global
* 
* # Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
* echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
* 
* # Apply the new PATH setting
* source ~/.bashrc
* 
* # Now reinstall Claude Code in the new location
* npm install -g @anthropic-ai/claude-code
* 
* # Optional: Reinstall your previous global packages in the new location
* # Look at ~/npm-global-packages.txt and install packages you want to keep
* This solution is recommended because it:
* 		Avoids modifying system directory permissions
* 		Creates a clean, dedicated location for your global npm packages
* 		Follows security best practices
* ​
* 
* System Recovery: If you have run commands that change ownership and permissions of system files or similar
* If you’ve already run a command that changed system directory permissions (such as sudo chown -R $USER:$(id -gn) /usr && sudo chmod -R u+w /usr) and your system is now broken (for example, if you see sudo: /usr/bin/sudo must be owned by uid 0 and have the setuid bit set), you’ll need to perform recovery steps.
* Ubuntu/Debian Recovery Method:
* While rebooting, hold SHIFT to access the GRUB menu
* Select “Advanced options for Ubuntu/Debian”
* Choose the recovery mode option
* Select “Drop to root shell prompt”
* Remount the filesystem as writable:Copymount -o remount,rw /
* 
* Fix permissions:Copy# Restore root ownership
* chown -R root:root /usr
* chmod -R 755 /usr
* 
* # Ensure /usr/local is owned by your user for npm packages
* chown -R YOUR_USERNAME:YOUR_USERNAME /usr/local
* 
* # Set setuid bit for critical binaries
* chmod u+s /usr/bin/sudo
* chmod 4755 /usr/bin/sudo
* chmod u+s /usr/bin/su
* chmod u+s /usr/bin/passwd
* chmod u+s /usr/bin/newgrp
* chmod u+s /usr/bin/gpasswd
* chmod u+s /usr/bin/chsh
* chmod u+s /usr/bin/chfn
* 
* # Fix sudo configuration
* chown root:root /usr/libexec/sudo/sudoers.so
* chmod 4755 /usr/libexec/sudo/sudoers.so
* chown root:root /etc/sudo.conf
* chmod 644 /etc/sudo.conf
* 
* Reinstall affected packages (optional but recommended):Copy# Save list of installed packages
* dpkg --get-selections > /tmp/installed_packages.txt
* 
* # Reinstall them
* awk '{print $1}' /tmp/installed_packages.txt | xargs -r apt-get install --reinstall -y
* 
* Reboot:Copyreboot
* 
* Alternative Live USB Recovery Method:
* If the recovery mode doesn’t work, you can use a live USB:
* Boot from a live USB (Ubuntu, Debian, or any Linux distribution)
* Find your system partition:Copylsblk
* 
* Mount your system partition:Copysudo mount /dev/sdXY /mnt  # replace sdXY with your actual system partition
* 
* If you have a separate boot partition, mount it too:Copysudo mount /dev/sdXZ /mnt/boot  # if needed
* 
* Chroot into your system:Copy# For Ubuntu/Debian:
* sudo chroot /mnt
* 
* # For Arch-based systems:
* sudo arch-chroot /mnt
* 
* Follow steps 6-8 from the Ubuntu/Debian recovery method above
* After restoring your system, follow the recommended solution above to set up a user-writable npm prefix.
* ​
* 
* Auto-updater issues
* If Claude Code can’t update automatically, it may be due to permission issues with your npm global prefix directory. Follow the recommended solution above to fix this.
* If you prefer to disable the auto-updater instead, you can use:
* 
* Copy
* claude config set -g autoUpdaterStatus disabled
* ​
* 
* Permissions and authentication
* ​
* 
* Repeated permission prompts
* If you find yourself repeatedly approving the same commands, you can allow specific tools to run without approval:
* 
* Copy
* # Let npm test run without approval
* claude config add allowedTools "Bash(npm test)"
* 
* # Let npm test and any of its sub-commands run without approval
* claude config add allowedTools "Bash(npm test:*)"
* ​
* 
* Authentication issues
* If you’re experiencing authentication problems:
* Run /logout to sign out completely
* Close Claude Code
* Restart with claude and complete the authentication process again
* If problems persist, try:
* 
* Copy
* rm -rf ~/.config/claude-code/auth.json
* claude
* This removes your stored authentication information and forces a clean login.
* ​
* 
* Performance and stability
* ​
* 
* High CPU or memory usage
* Claude Code is designed to work with most development environments, but may consume significant resources when processing large codebases. If you’re experiencing performance issues:
* Use /compact regularly to reduce context size
* Close and restart Claude Code between major tasks
* Consider adding large build directories to your .gitignore file
* ​
* 
* Command hangs or freezes
* If Claude Code seems unresponsive:
* Press Ctrl+C to attempt to cancel the current operation
* If unresponsive, you may need to close the terminal and restart
* ​
* 
* ESC key not working in JetBrains (IntelliJ, PyCharm, etc.) terminals
* If you’re using Claude Code in JetBrains terminals and the ESC key doesn’t interrupt the agent as expected, this is likely due to a keybinding clash with JetBrains’ default shortcuts.
* To fix this issue:
* Go to Settings → Tools → Terminal
* Click the “Configure terminal keybindings” hyperlink next to “Override IDE Shortcuts”
* Within the terminal keybindings, scroll down to “Switch focus to Editor” and delete that shortcut
* This will allow the ESC key to properly function for canceling Claude Code operations instead of being captured by PyCharm’s “Switch focus to Editor” action.
* ​
* 
* Getting more help
* If you’re experiencing issues not covered here:
* Use the /bug command within Claude Code to report problems directly to Anthropic
* Check the GitHub repository for known issues
* 	3	Run /doctor to check the health of your Claude Code installation

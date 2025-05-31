import os
import subprocess
import json
from typing import Dict, Any, List, Union
from crewai.tools import BaseTool
import matplotlib.pyplot as plt
import psutil
import git

# --- Configuration Management Tool ---
class EnvironmentVariableTool(BaseTool):
    name: str = "Environment Variable Tool"
    description: str = (
        "Manages environment variables. "
        "Input should be a dictionary with 'action' ('get', 'set', 'list', 'unset'), "
        "'name' (for get, set, unset), and 'value' (for set)."
    )

    def _run(self, argument: Dict[str, Any]) -> str:
        action = argument.get("action")
        name = argument.get("name")
        value = argument.get("value")

        if action == "get":
            if not name:
                return "Error: 'name' is required for 'get' action."
            return os.environ.get(name, f"Variable {name} not found.")
        elif action == "set":
            if not name or value is None:
                return "Error: 'name' and 'value' are required for 'set' action."
            os.environ[name] = str(value)
            return f"Environment variable {name} set."
        elif action == "list":
            return json.dumps(dict(os.environ), indent=2)
        elif action == "unset":
            if not name:
                return "Error: 'name' is required for 'unset' action."
            if name in os.environ:
                del os.environ[name]
                return f"Environment variable {name} unset."
            return f"Variable {name} not found."
        else:
            return "Error: Invalid action. Must be 'get', 'set', 'list', or 'unset'."

# --- Security Tool ---
class StaticCodeAnalysisTool(BaseTool):
    name: str = "Static Code Analysis Tool"
    description: str = (
        "Performs basic static analysis on a Python file using bandit. "
        "Input should be the path to the Python file."
    )

    def _run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        if not file_path.endswith(".py"):
            return "Error: Tool currently only supports Python files (.py)"
        try:
            # Ensure bandit is installed or handle gracefully
            process = subprocess.run(
                ["bandit", "-r", file_path, "-f", "json"],
                capture_output=True, text=True, check=True
            )
            return process.stdout
        except FileNotFoundError:
            return "Error: bandit tool not found. Please ensure it's installed and in PATH."
        except subprocess.CalledProcessError as e:
            return f"Error during static analysis: {e.stderr}"

# --- Git Management Tool ---
class GitManagementTool(BaseTool):
    name: str = "Git Management Tool"
    description: str = (
        "Interacts with Git repositories. "
        "Input: dictionary with 'action' ('status', 'clone', 'pull', 'push', 'commit', 'branch', 'checkout'), "
        "'repo_path' (for most actions, defaults to current dir), 'remote_url' (for clone), "
        "'message' (for commit), 'branch_name' (for branch/checkout)."
    )

    def _get_repo(self, repo_path: str = None) -> Union[git.Repo, str]:
        try:
            path = repo_path or os.getcwd()
            return git.Repo(path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            return f"Error: Not a git repository (or any of the parent directories): {path}"
        except Exception as e:
            return f"Error accessing repository at {path}: {str(e)}"

    def _run(self, argument: Dict[str, Any]) -> str:
        action = argument.get("action")
        repo_path = argument.get("repo_path", os.getcwd()) # Default to CWD

        if action == "clone":
            remote_url = argument.get("remote_url")
            if not remote_url:
                return "Error: 'remote_url' is required for 'clone'."
            try:
                git.Repo.clone_from(remote_url, repo_path)
                return f"Repository cloned from {remote_url} to {repo_path}."
            except Exception as e:
                return f"Error cloning repository: {str(e)}"

        repo = self._get_repo(repo_path)
        if isinstance(repo, str): # Error message from _get_repo
            return repo

        try:
            if action == "status":
                return repo.git.status()
            elif action == "pull":
                return repo.git.pull()
            elif action == "push":
                return repo.git.push()
            elif action == "commit":
                message = argument.get("message")
                if not message:
                    return "Error: 'message' is required for 'commit'."
                # Add all changes before commit for simplicity, or specify files
                repo.git.add(A=True)
                return repo.git.commit(m=message)
            elif action == "branch":
                branch_name = argument.get("branch_name")
                if branch_name:
                    return repo.git.branch(branch_name)
                return repo.git.branch() # List branches
            elif action == "checkout":
                branch_name = argument.get("branch_name")
                if not branch_name:
                    return "Error: 'branch_name' is required for 'checkout'."
                return repo.git.checkout(branch_name)
            else:
                return "Error: Invalid Git action."
        except git.GitCommandError as e:
            return f"Git command error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred with Git: {str(e)}"


# --- Network Diagnostic Tool ---
class NetworkDiagnosticTool(BaseTool):
    name: str = "Network Diagnostic Tool"
    description: str = (
        "Performs network diagnostics like ping, traceroute, nslookup. "
        "Input: dictionary with 'action' ('ping', 'traceroute', 'nslookup') and 'host'."
        "For 'ping', can also include 'count' (optional, default 4)."
    )

    def _run(self, argument: Dict[str, Any]) -> str:
        action = argument.get("action")
        host = argument.get("host")
        if not host:
            return "Error: 'host' is required."

        try:
            if action == "ping":
                count = argument.get("count", 4)
                cmd = ["ping", "-c" if os.name != "nt" else "-n", str(count), host]
            elif action == "traceroute":
                cmd = ["traceroute" if os.name != "nt" else "tracert", host]
            elif action == "nslookup":
                cmd = ["nslookup", host]
            else:
                return "Error: Invalid action. Must be 'ping', 'traceroute', or 'nslookup'."

            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if process.returncode == 0:
                return process.stdout
            else:
                return f"Error executing {action}: {process.stderr or process.stdout}"
        except subprocess.TimeoutExpired:
            return f"Error: {action} to {host} timed out."
        except FileNotFoundError:
            return f"Error: {cmd[0]} command not found. Please ensure it's installed."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

# --- Data Visualization Tool ---
class PlottingTool(BaseTool):
    name: str = "Plotting Tool"
    description: str = (
        "Generates simple plots (line, bar) from data and saves as an image. "
        "Input: dictionary with 'plot_type' ('line', 'bar'), 'data' (list of numbers or dict for bar), "
        "'x_labels' (optional for line/bar), 'title', 'x_axis_label', 'y_axis_label', 'output_filename' (e.g., plot.png)."
    )

    def _run(self, argument: Dict[str, Any]) -> str:
        plot_type = argument.get("plot_type")
        data = argument.get("data")
        title = argument.get("title", "Plot")
        x_label = argument.get("x_axis_label", "X-axis")
        y_label = argument.get("y_axis_label", "Y-axis")
        output_filename = argument.get("output_filename", "plot.png")
        x_labels = argument.get("x_labels")

        if not plot_type or data is None:
            return "Error: 'plot_type' and 'data' are required."

        plt.figure()
        try:
            if plot_type == "line":
                if x_labels and len(x_labels) == len(data):
                    plt.plot(x_labels, data)
                else:
                    plt.plot(data)
            elif plot_type == "bar":
                if isinstance(data, dict):
                    names = list(data.keys())
                    values = list(data.values())
                    plt.bar(names, values)
                elif isinstance(data, list):
                    if x_labels and len(x_labels) == len(data):
                        plt.bar(x_labels, data)
                    else:
                        plt.bar(range(len(data)), data)
                else:
                    return "Error: 'data' for bar plot must be a list or dictionary."
            else:
                return "Error: Invalid 'plot_type'. Must be 'line' or 'bar'."

            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.savefig(output_filename)
            plt.close() # Close the plot to free memory
            return f"Plot saved as {output_filename}"
        except Exception as e:
            plt.close()
            return f"Error generating plot: {str(e)}"

# --- System Monitoring Tool ---
class SystemMonitoringTool(BaseTool):
    name: str = "System Monitoring Tool"
    description: str = (
        "Provides system monitoring information like CPU usage, memory usage, disk usage, and network stats. "
        "Input: dictionary with 'query' ('cpu', 'memory', 'disk', 'network_io', 'processes'). "
        "For 'disk', can specify 'path' (optional, default '/'). "
        "For 'processes', can specify 'sort_by' (optional, e.g., 'cpu_percent', 'memory_percent') and 'limit' (optional, default 10)."
    )

    def _run(self, argument: Dict[str, Any]) -> str:
        query = argument.get("query")
        try:
            if query == "cpu":
                return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"
            elif query == "memory":
                mem = psutil.virtual_memory()
                return json.dumps({
                    "total": f"{mem.total / (1024**3):.2f} GB",
                    "available": f"{mem.available / (1024**3):.2f} GB",
                    "percent_used": f"{mem.percent}%",
                    "used": f"{mem.used / (1024**3):.2f} GB",
                    "free": f"{mem.free / (1024**3):.2f} GB",
                }, indent=2)
            elif query == "disk":
                path = argument.get("path", "/")
                disk = psutil.disk_usage(path)
                return json.dumps({
                    "path": path,
                    "total": f"{disk.total / (1024**3):.2f} GB",
                    "used": f"{disk.used / (1024**3):.2f} GB",
                    "free": f"{disk.free / (1024**3):.2f} GB",
                    "percent_used": f"{disk.percent}%",
                }, indent=2)
            elif query == "network_io":
                net_io = psutil.net_io_counters()
                return json.dumps({
                    "bytes_sent": f"{net_io.bytes_sent / (1024**2):.2f} MB",
                    "bytes_recv": f"{net_io.bytes_recv / (1024**2):.2f} MB",
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                }, indent=2)
            elif query == "processes":
                sort_by = argument.get("sort_by", "cpu_percent")
                limit = argument.get("limit", 10)
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Filter out kernel tasks or similar if username is not available or empty
                processes = [p for p in processes if p.get('username')]

                if sort_by not in ['pid', 'name', 'username', 'cpu_percent', 'memory_percent']:
                    sort_by = 'cpu_percent' # default sort if invalid
                
                # Handle cases where sort_by key might be missing for some processes
                processes.sort(key=lambda p: p.get(sort_by, 0) if isinstance(p.get(sort_by), (int, float)) else 0, reverse=True)
                return json.dumps(processes[:limit], indent=2)
            else:
                return "Error: Invalid query. Must be 'cpu', 'memory', 'disk', 'network_io', or 'processes'."
        except Exception as e:
            return f"Error getting system info for '{query}': {str(e)}"

# Note: PersistentKeyValueStoreTool and UserPreferenceTool would require a backend (e.g., SQLite, file).
# For simplicity, they are omitted here but would be crucial for long-term context and personalization.

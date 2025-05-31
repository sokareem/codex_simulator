from setuptools import setup, find_packages

setup(
    name="codex_simulator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai[tools]>=0.86.0,<1.0.0",
        "argparse>=1.4.0",
        "langchain-google-genai>=0.0.1",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "codex-simulator=codex_simulator.main:run",
            "codex-terminal=codex_simulator.main:run_terminal_assistant_with_flows",
        ],
    },
    python_requires=">=3.10,<=3.13",
)

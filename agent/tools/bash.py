import subprocess
from langchain_core.tools import tool

@tool
def bash_tool(command: str):
    """
    Run a bash command and return its exit code, stdout and stderr.
    :param command: The bash command to run
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
    except subprocess.TimeoutExpired:
        return "exit_code: timeout\nCommand timed out after 30 seconds."
    return (
        f"exit_code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
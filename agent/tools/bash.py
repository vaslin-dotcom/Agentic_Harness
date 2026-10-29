import subprocess
from langchain_core.tools import tool

@tool
def bash_tool(command:str):
    """
    This is a function to run a bash command
    The parameters is:
    :param command:The bash command to run
    This function returns the output of the bash command
    """
    result=subprocess.run(command,shell=True,capture_output=True,text=True)
    return result.stdout or result.stderr
from agent.tools.bash import bash_tool
from agent.tools.files import read_file,write_file,replace_file

tools=[bash_tool,read_file,write_file,replace_file]
tool_map = {t.name: t for t in tools}
import os
import platform
from datetime import date
from pathlib import Path
from agent.prompts import system_prompt

working_directory = r'C:\Users\anton\PycharmProjects\Agentic_Harness\working_directory'

def build_environment_block() -> str:
    on_windows = os.name == "nt"
    # subprocess(shell=True) uses cmd.exe on Windows and /bin/sh elsewhere
    shell = os.environ.get("COMSPEC", "cmd.exe") if on_windows else "/bin/sh"

    lines = [
        "ENVIRONMENT (generated at session start, trust this over your assumptions):",
        f"- Working directory: '{working_directory}'",
        f"- Operating system: {platform.platform()}",
        f"- Shell used by bash_tool: {shell}",
        f"- Today's date: {date.today().isoformat()}",
    ]
    if on_windows:
        lines.append("- bash_tool runs Windows cmd commands, not Linux commands (use dir, not ls).")
    return "\n".join(lines)




MAX_PROJECT_CHARS = 8000
INSTRUCTION_FILES = ["AGENTS.md"]

def load_project_instructions() -> str:
    for name in INSTRUCTION_FILES:
        path = Path(working_directory) / name
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if len(text) > MAX_PROJECT_CHARS:
                extra = len(text) - MAX_PROJECT_CHARS
                text = text[:MAX_PROJECT_CHARS] + f"\n... [truncated, {extra} more chars, read {name} for the rest]"
            return f"PROJECT INSTRUCTIONS (from {name}):\n{text}"
    return ""

def build_system_prompt() -> str:
    parts = [system_prompt.strip(), build_environment_block()]
    project = load_project_instructions()
    if project:
        parts.append(project)
    return "\n\n".join(parts)
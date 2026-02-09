import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from main import edit_file_tool, list_files_tool, read_file_tool

TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "list_files": list_files_tool,
    "edit_file": edit_file_tool,
}


def get_tool_str_representation(tool_name: str) -> str:
    tool = TOOL_REGISTRY[tool_name]
    return f"""
    Name: {tool_name}
    Description: {tool.__doc__}
    Signature: {inspect.signature(tool)}
    """


def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return list of (tool_name, args) requested in 'tool: name({...})' lines.
    The parser expects single-line, compact JSON in parentheses.
    """
    invocations = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("tool:"):
            continue
        try:
            after = line[len("tool:") :].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations


SYSTEM_PROMPT = """ 
You are a coding assistant whose goal it is to help us solve coding tasks.
You have access to a series of tools you can execute. Here are the tools you can execute:

{tool_list_repr}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
"""


def get_full_system_prompt():
    tool_str_repr = ""
    for tool_name in TOOL_REGISTRY:
        tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool_name)
        tool_str_repr += f"\n{'=' * 15}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)


def load_prompt(file_path):
    """Loads a prompt from a markdown file."""
    prompt = Path(file_path).read_text()
    return prompt


def collect_code_to_context(project_path: str, output_file: str):
    root = Path(project_path)

    with open(output_file, "w") as out:
        out.write(f"# Java files - {root}\n\n")

        for path in sorted(root.rglob("*.java")):
            out.write(f"## `{path.relative_to(root)}`\n\n")
            out.write(f"```java\n{path.read_text()}\n```\n\n")

    print(f"Done → {output_file}")


def build_prompt(context_paths, output_file):
    """Combine prompt parts into single prompt."""
    combined_prompt = []
    for path in context_paths:
        combined_prompt.append(load_prompt(path))

    with open(output_file, "w") as out:
        out.write("\n".join(combined_prompt))

    print(f"Done → {output_file}")


def resolve_abs_path(path_str: str) -> Path:
    """
    Resolves a relative path to an absolute path.
    """
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path

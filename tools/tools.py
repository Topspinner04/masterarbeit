from pathlib import Path
from typing import Any, Dict
from config import GENERATED_PATH, REF_PATH


def read_file_tool(filename: str) -> Dict[str, Any]:
    """Gets the full content of a file provided by the user.
    :param filename: The name of the file to read.
    :return: The full content of the file.
    """
    project_path = Path(
        REF_PATH
    ).resolve()  # Only let the agent read files within the ref directory
    full_path = (project_path / filename).resolve()
    print(full_path)
    with open(str(full_path), "r") as f:
        content = f.read()
    return {"file_path": str(full_path), "content": content}


def list_files_tool(path: str) -> Dict[str, Any]:
    """Lists the files in a directory provided by the user.
    :param path: The path to a directory to list files from.
    :return: A list of files in the directory.
    """
    project_path = Path(
        REF_PATH
    ).resolve()  # Only let the agent list files within the ref directory
    full_path = (project_path / path).resolve()
    all_files = []
    for item in full_path.iterdir():
        all_files.append(
            {"filename": item.name, "type": "file" if item.is_file() else "dir"}
        )
    return {"path": str(full_path), "files": all_files}


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """Replaces first occurrence of old_str with new_str in file. If old_str is empty,
    create/overwrite file with new_str.
    :param path: The path to the file to edit.
    :param old_str: The string to replace.
    :param new_str: The string to replace with.
    :return: A dictionary with the path to the file and the action taken.
    """
    # Only let the agent read files within the ref directory
    project_path = Path(REF_PATH).resolve()
    full_path = project_path / path

    # Only let the agent store created and modified files within the generated directory
    generated_path = Path(GENERATED_PATH).resolve()
    new_path = generated_path / path

    if old_str == "":
        new_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # creates the parent directories if they don't exist
        new_path.write_text(new_str, encoding="utf-8")
        return {"path": str(new_path), "action": "created_file"}
    original = full_path.read_text(encoding="utf-8")
    if original.find(old_str) == -1:
        return {"path": str(full_path), "action": "old_str not found"}
    edited = original.replace(old_str, new_str, 1)
    new_path.write_text(edited, encoding="utf-8")
    return {"path": str(new_path), "action": "edited"}

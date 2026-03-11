from pathlib import Path
from typing import Any, Dict
from config import GEN_PATH, REF_PATH


def read_file_tool(path: str) -> Dict[str, Any]:
    """Gets the full content of a file provided by the user.
    :param path: The path to the file to read.
    :return: The full content of the file.
    """
    ref_root = Path(REF_PATH).resolve()
    ref_path = ref_root / path

    with open(str(ref_path), "r") as f:
        content = f.read()
    return {"file_path": str(ref_path), "content": content}


def list_files_tool(path: str) -> Dict[str, Any]:
    """Lists the files in a directory provided by the user.
    :param path: The path to a directory to list files from.
    :return: A list of files in the directory.
    """
    ref_root = Path(REF_PATH).resolve()
    ref_path = ref_root / path

    if not ref_path.exists():
        return {"path": str(ref_path), "error": "path_not_found", "files": []}

    # Fallback if path is not a directory
    if not ref_path.is_dir():
        return {"path": str(ref_path), "error": "not_a_directory", "files": []}

    all_files = []
    for item in ref_path.iterdir():
        all_files.append(
            {"filename": item.name, "type": "file" if item.is_file() else "dir"}
        )
    return {"path": str(ref_path), "files": all_files}


def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """Replaces first occurrence of old_str with new_str in file. If old_str is empty,
    create/overwrite file with new_str.
    :param path: The path to the file to edit.
    :param old_str: The string to replace.
    :param new_str: The string to replace with.
    :return: A dictionary with the path to the file and the action taken.
    """
    # Only let the agent read files within the ref directory
    ref_root = Path(REF_PATH).resolve()
    ref_file = ref_root / path

    # case new file
    if old_str == "":
        ref_file.parent.mkdir(
            parents=True, exist_ok=True
        )  # creates the parent directories if they don't exist
        ref_file.write_text(new_str, encoding="utf-8")
        return {"path": str(ref_file), "action": "created_file"}

    # case edit file
    if not ref_file.exists():
        return {"path": str(ref_file), "action": "file_not_found"}

    content = ref_file.read_text(encoding="utf-8")

    if content.find(old_str) == -1:
        return {"path": str(content), "action": "str_not_found"}

    edited_content = content.replace(old_str, new_str, 1)
    ref_file.parent.mkdir(parents=True, exist_ok=True)
    ref_file.write_text(edited_content, encoding="utf-8")
    return {"path": str(ref_file), "action": "edited_file"}

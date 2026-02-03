from pathlib import Path


def load_prompt(file_path):
    """Loads a prompt from a markdown file."""
    prompt = Path(file_path).read_text()
    return prompt


def collect_code_to_context(project_path: str, output_file: str):
    root = Path(project_path)

    with open(output_file, "w") as out:
        out.write(f"# Python files - {root}\n\n")

        for path in sorted(root.rglob("*.py")):
            out.write(f"## `{path.relative_to(root)}`\n\n")
            out.write(f"```python\n{path.read_text()}\n```\n\n")

    print(f"Done → {output_file}")


def build_prompt_from_context(context_paths, output_file):
    """Combine prompt parts into single prompt."""
    combined_prompt = []
    for path in context_paths:
        combined_prompt.append(load_prompt(path))

    with open(output_file, "w") as out:
        out.write("\n".join(combined_prompt))

    print(f"Done → {output_file}")

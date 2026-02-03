from pathlib import Path


def load_prompt(filepath):
    """Loads a prompt from a markdown file."""
    prompt = Path(filepath).read_text()
    return prompt


# TODO: Add functionality to ignore unneccessary files
def collect_code_to_context(folder_path, output_file):
    """Collect all relevant files from a project into a single markdown file."""
    folder = Path(folder_path)

    with open(output_file, "w") as out:
        out.write(f"# Code files from {folder_path}\n\n")

        for file_path in folder.rglob("*"):
            if file_path.is_dir():
                continue

            rel_path = file_path.relative_to(folder)
            try:
                with open(file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                content = f"Could not read file: {e}"

            lang = file_path.suffix.lstrip(".")

            out.write(f"## {file_path}\n\n")
            out.write(f"**Path:** {rel_path}\n\n")
            out.write(f"```{lang}\n{content}\n```\n\n")
            out.write("---\n\n")


def build_prompt_from_context(context_paths, output_file):
    """Combine prompt parts into single prompt."""
    combined_prompt = []
    for path in context_paths:
        combined_prompt.append(load_prompt(path))

    with open(output_file, "w") as out:
        out.write("\n".join(combined_prompt))

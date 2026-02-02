from pathlib import Path


def load_prompt(filepath):
    """Load a prompt from a text file."""
    prompt = Path(filepath).read_text()
    return prompt

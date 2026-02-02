from utils import load_prompt

system_prompt = load_prompt("prompts/system.md")
task_prompt = load_prompt("prompts/what2eat/task.md")


def build_prompt(prompt_paths):
    """Combine prompt parts into single prompt."""
    combined_prompt = []
    for path in prompt_paths:
        combined_prompt.append(load_prompt(path))

    return "\n".join(combined_prompt)

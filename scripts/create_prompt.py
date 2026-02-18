from utils.utils import build_prompt
from config import CONTEXT_PATH, PROMPT_PATH, TREATMENT


# Build context prompt from architecture documentation for both treatments
build_prompt(
    context_paths=[f"{CONTEXT_PATH}/{TREATMENT}.md"],
    output_file=f"{PROMPT_PATH}/context.md",
)

# Build user prompt from task and context prompt for both treatments
build_prompt(
    context_paths=[
        f"{PROMPT_PATH}/task.md",
        f"{PROMPT_PATH}/context.md",
    ],
    output_file=f"{PROMPT_PATH}/user.md",
)

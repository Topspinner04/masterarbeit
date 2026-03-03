from utils.utils import build_prompt
from config import PROMPT_PATH


# Build user prompt from task and context prompt
build_prompt(
    context_paths=[
        f"{PROMPT_PATH}/context.md",
        f"{PROMPT_PATH}/task.md",
    ],
    output_file=f"{PROMPT_PATH}/user.md",
)

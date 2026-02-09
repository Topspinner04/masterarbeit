from utils.utils import build_prompt, collect_code_to_context
from config import REF_PATH, CONTEXT_PATH, PROMPT_PATH

# Collect code files from ref to code context markdown file
code_context = collect_code_to_context(
    project_path=REF_PATH,
    output_file=f"{CONTEXT_PATH}/code_context.md",
)

# Build context prompt from code context and architecture documentation
build_prompt(
    context_paths=[
        f"{CONTEXT_PATH}/code_context.md",
        f"{CONTEXT_PATH}/architecture_documentation.md",
    ],
    output_file=f"{PROMPT_PATH}/context.md",
)

# Build user prompt from task and context prompt
build_prompt(
    context_paths=[
        f"{PROMPT_PATH}/task.md",
        f"{PROMPT_PATH}/context.md",
    ],
    output_file=f"{PROMPT_PATH}/user.md",
)

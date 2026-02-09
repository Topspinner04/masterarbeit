from utils.utils import build_prompt
from config import CONTEXT_PATH, PROMPT_PATH

"""
No longer needed as we have an agent with tools now

# Collect code files from ref to code context markdown file
code_context = collect_code_to_context(
    project_path=REF_PATH,
    output_file=f"{CONTEXT_PATH}/code_context.md",
)
"""

# Build context prompt from architecture documentation
# Right now just takes all of the documentation provided in the context
build_prompt(
    context_paths=[f"{CONTEXT_PATH}/architecture_documentation.md"],
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

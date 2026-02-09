# Collects code files from ref to code context markdown file
from utils.utils import build_prompt, collect_code_to_context


# Set up project and paths. To change projects just change the project name.
project = "what2eat"
ref_path = f"ref/{project}"
context_path = f"context/{project}"
prompt_path = f"prompts/{project}"

code_context = collect_code_to_context(
    project_path=ref_path,
    output_file=f"{context_path}/code_context.md",
)

# Build context prompt from code context and architecture documentation
build_prompt(
    context_paths=[
        f"{context_path}/code_context.md",
        f"{context_path}/architecture_documentation.md",
    ],
    output_file=f"{prompt_path}/context.md",
)

# Build user prompt from task and context prompt
build_prompt(
    context_paths=[
        f"{prompt_path}/task.md",
        f"{prompt_path}/context.md",
    ],
    output_file=f"{prompt_path}/user.md",
)

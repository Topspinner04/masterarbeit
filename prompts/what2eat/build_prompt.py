from utils.utils import build_prompt_from_parts

build_prompt_from_parts(
    prompt_paths=[
        "prompts/what2eat/task.md",
        "prompts/what2eat/context.md",
    ],
    output_file="prompts/what2eat/prompt.md",
)

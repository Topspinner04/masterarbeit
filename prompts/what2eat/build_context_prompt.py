from utils.utils import build_prompt_from_parts

build_prompt_from_parts(
    prompt_paths=[
        "prompts/what2eat/context-code/context_code.md",
        "prompts/what2eat/context-documentation/architecture-documentation.md",
    ],
    output_file="prompts/what2eat/context.md",
)

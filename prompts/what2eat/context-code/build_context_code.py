from utils.utils import collect_code_to_markdown

code_prompt = collect_code_to_markdown(
    folder_path="prompts/what2eat/context-code/what2eat/src",
    output_file="prompts/what2eat/context-code/context_code.md",
)

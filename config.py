PROJECT = "what2eat"
TREATMENT = "treatment_a"  # or "treatment_b"
REF_PATH = (
    f"ref/{PROJECT}/{PROJECT}"  # tool can only access source code for now and not docs
)
GENERATED_PATH = f"generated/{PROJECT}/{TREATMENT}"
PROMPT_PATH = f"prompts/{PROJECT}/{TREATMENT}"

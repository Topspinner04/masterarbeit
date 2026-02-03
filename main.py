import logfire
from pydantic_ai import Agent
from dotenv import load_dotenv
from utils.utils import build_prompt, collect_code_to_context, load_prompt

# Load environment variables from .env file
load_dotenv()

# Set up logging and instrumentation
logfire.configure()
logfire.instrument_pydantic_ai()

# Set up project and paths. To change projects just change the project name.
project = "what2eat"
ref_path = f"ref/{project}"
context_path = f"context/{project}"
prompt_path = f"prompts/{project}"

# Collects code files from ref to code context markdown file
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

# Load system prompt
system_prompt = load_prompt("prompts/system.md")

# Load user prompt
user_prompt = load_prompt(f"{prompt_path}/user.md")

agent = Agent(
    "google-gla:gemini-2.5-pro",
    instructions=system_prompt,
)

result = agent.run_sync(user_prompt)

print(result.output)

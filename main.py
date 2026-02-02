from pydantic_ai import Agent
from dotenv import load_dotenv
from utils import load_prompt
from prompts.what2eat.build_prompt import build_prompt
import logfire

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

system_prompt = load_prompt("prompts/system.md")
prompt = build_prompt(
    [
        "prompts/system.md",
        "prompts/what2eat/task.md",
    ]
)

agent = Agent(
    "google-gla:gemini-2.5-pro",
    instructions=system_prompt,
)

result = agent.run_sync(prompt)

print(result.output)

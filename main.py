from pydantic_ai import Agent
from dotenv import load_dotenv
from utils.utils import load_prompt

import logfire

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

system_prompt = load_prompt("prompts/system.md")
prompt = load_prompt("prompts/what2eat/prompt.md")

agent = Agent(
    "google-gla:gemini-2.5-pro",
    instructions=system_prompt,
)

result = agent.run_sync(prompt)

print(result.output)

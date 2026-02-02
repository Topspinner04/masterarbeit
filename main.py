from pydantic_ai import Agent
from dotenv import load_dotenv
from utils import load_prompt
import logfire

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

system_prompt = load_prompt("prompts/system.md")

agent = Agent(
    "google-gla:gemini-2.5-pro",
    instructions=system_prompt,
)

result = agent.run_sync(
    """
    def add_numbers(a: int, b: int) -> int:
    
    "
        Add two integers and return their sum.

        Args:
            a (int): The first integer.
            b (int): The second integer.

        Returns:
            int: The sum of a and b.

        Raises:
            TypeError: If either argument is not an integer.
    "
    """
)
print(result.output)

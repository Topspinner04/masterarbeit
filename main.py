from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from dotenv import load_dotenv
from config import GEN_PATH, MODEL, PROMPT_PATH, REF_PATH, TREATMENT
from rag.retriever import Retriever
from rag.embedder import Embedder
from rag.rag_tool import RAGTool
from rag.vector_store import VectorStore
from utils.utils import copy_submodule_and_reset, load_prompt
from tools.tools import read_file_tool, list_files_tool, edit_file_tool

import logfire

# Load environment variables from .env file
load_dotenv()

# Set up logging and instrumentation
logfire.configure()
logfire.instrument_pydantic_ai()

# Load existing index
vector_store = VectorStore.load("rag/vector_store")

# Create embedder
embedder = Embedder()

# Create retriever
retriever = Retriever(embedder, vector_store)

# Create RAG tool
rag_tool = RAGTool(retriever)

# Load system prompt
system_prompt = load_prompt(f"{PROMPT_PATH}/{TREATMENT}/system.md")

# Local Qwen3 Coder
model_Qwen = OpenAIChatModel(
    model_name="llm",
    provider=OpenAIProvider(
        base_url="https://blackwell.iese.de/qwen_3_coder_480b_a35b_instruct/v1",
        api_key="sk-vllm",
    ),
)

# Google AI studio Gemini
model_Gemini = "google-gla:gemini-3-flash-preview"

# Set model according to config
if MODEL == "Qwen":
    model = model_Qwen
else:
    model = model_Gemini

agent = Agent(
    model=model,
    instructions=system_prompt,
    tools=[
        read_file_tool,
        list_files_tool,
        edit_file_tool,
    ],
)

rag_agent = Agent(
    model=model,
    instructions=system_prompt,
    tools=[
        rag_tool.perform_rag_search,
        read_file_tool,
        list_files_tool,
        edit_file_tool,
    ],
)


def main():
    # Load user prompt from project
    user_prompt = load_prompt(f"{PROMPT_PATH}/{TREATMENT}/user.md")

    # Run agent and print results
    if TREATMENT in ["treatment_a", "treatment_b", "treatment_d"]:  # these do not use RAG. a with no context, b with full context in prompt
        print(f"Performing treatment with agent and {model}")
        result = agent.run_sync(user_prompt)
    else:
        print(f"Performing treatment with rag_agent and {model}")
        result = rag_agent.run_sync(user_prompt)

    print(result.output)
    # Copies edited files to gen/ and resets ref/ to baseline
    copy_submodule_and_reset(".", REF_PATH, GEN_PATH)


if __name__ == "__main__":
    main()

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from dotenv import load_dotenv
from config import PROMPT_PATH, REF_PATH
from rag.retriever import Retriever
from rag.chunk import Chunker
from rag.embedder import Embedder
from rag.rag_tool import RAGTool
from rag.vector_store import VectorStore
from utils.utils import load_prompt
from tools.tools import read_file_tool, list_files_tool, edit_file_tool

import logfire

# Load environment variables from .env file
load_dotenv()

# Set up logging and instrumentation
logfire.configure()
logfire.instrument_pydantic_ai()

# Load and chunk architecture documentation
with open(f"{REF_PATH}/docs/architecture.md", "r", encoding="utf-8") as f:
    doc = f.read()

chunker = Chunker()
docs = chunker.chunk(doc)

# Embedd chunks
embedder = Embedder()
embeddings = embedder.embed([doc.content for doc in docs])

# Add embeddings and corresponding chunks to vector store
vector_store = VectorStore(dim=embeddings.shape[1])
vector_store.add(embeddings, docs)

# Create retriever and RAG tool
retriever = Retriever(embedder, vector_store)
rag_tool = RAGTool(retriever)

# Load system prompt
system_prompt = load_prompt("prompts/system.md")

# Local Qwen3 Coder
model = OpenAIChatModel(
    model_name='llm',
    provider=OpenAIProvider(
        base_url='https://blackwell.iese.de/qwen_3_coder_480b_a35b_instruct/v1', api_key='sk-vllm'
    ),
)
agent = Agent(model)

# Cloud Gemini AI 
agent_cloud = Agent(
    "google-gla:gemini-2.5-pro",
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
    user_prompt = load_prompt(f"{PROMPT_PATH}/user.md")

    # Rund agent and print results
    result = agent.run_sync(user_prompt)
    print(result.output)


if __name__ == "__main__":
    main()

from config import DOC_PATH
from rag.retriever import Retriever
from rag.chunk import Chunker
from rag.embedder import Embedder
from rag.vector_store import VectorStore


# Load and chunk architecture documentation
with open(f"{DOC_PATH}/architecture.md", "r", encoding="utf-8") as f:
    doc = f.read()

chunker = Chunker()
docs = chunker.chunk(doc)

# Create embeddings
embedder = Embedder()
embeddings = embedder.embed([doc.content for doc in docs])

# Create vector store and add embeddings
vector_store = VectorStore(dim=embeddings.shape[1])
vector_store.add(embeddings, docs)

# Save vector store
vector_store.save("rag/vector_store")

print(f"Index saved to rag/vector_store")
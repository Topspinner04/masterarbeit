from .embedder import Embedder
from .vector_store import VectorStore


class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 3):
        query_emb = self.embedder.embed([query])
        return self.vector_store.search(query_emb, k=k)

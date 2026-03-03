import faiss
import numpy as np
from typing import List
from .document import Document

class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.documents: List[Document] = []

    def add(self, embeddings: np.ndarray, docs: List[Document]):
        self.index.add(embeddings) # type: ignore
        self.documents.extend(docs)

    def search(self, query_embedding: np.ndarray, k: int = 3):
        distances, indices = self.index.search(query_embedding, k) # type: ignore
        return [self.documents[i] for i in indices[0]]
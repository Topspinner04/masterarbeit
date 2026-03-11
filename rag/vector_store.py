import faiss
import pickle
import numpy as np
from typing import List

from .document import Document


class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.documents: List[Document] = []

    def add(self, embeddings: np.ndarray, docs: List[Document]):
        self.index.add(embeddings)  # type: ignore
        self.documents.extend(docs)

    def search(self, query_embedding: np.ndarray, k: int = 3):
        distances, indices = self.index.search(query_embedding, k)  # type: ignore
        return [self.documents[i] for i in indices[0]]

    def save(self, path: str):
        """Save FAISS index and documents."""
        faiss.write_index(self.index, f"{path}/index.faiss")

        with open(f"{path}/docs.pkl", "wb") as f:
            pickle.dump(self.documents, f)

    @classmethod
    def load(cls, path: str):
        """Load FAISS index and documents."""
        index = faiss.read_index(f"{path}/index.faiss")

        with open(f"{path}/docs.pkl", "rb") as f:
            documents = pickle.load(f)

        dim = index.d
        store = cls(dim)
        store.index = index
        store.documents = documents

        return store
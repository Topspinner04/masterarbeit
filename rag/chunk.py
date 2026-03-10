from typing import List
from .document import Document


class Chunker:
    def __init__(self) -> None:
        pass

    def chunk(self, document: str, chunk_size=1024, overlap=128) -> List[Document]:
        docs = []
        start = 0

        while start < len(document):
            end = start + chunk_size
            content = document[start:end]
            docs.append(
                Document(
                    content=content,
                    metadata={"start_char": start, "end_char": min(end, len(document))},
                )
            )
            start += chunk_size - overlap

        return docs

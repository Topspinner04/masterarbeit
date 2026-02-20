import re
from typing import List
from .document import Document


class Chunker:
    def __init__(self) -> None:
        pass

    def chunk(self, document: str) -> List[Document]:
        # Split on any markdown heading (# to ######)
        pattern = r"(?m)^(#{1,6}) (.+)$"
        matches = list(re.finditer(pattern, document))

        docs = []
        for i, match in enumerate(matches):
            heading_text = match.group(2).strip()

            # Determine the end: start of next heading or end of document
            end = matches[i + 1].start() if i + 1 < len(matches) else len(document)
            content = document[
                match.start() : end
            ].strip()  # include heading in content

            docs.append(
                Document(
                    content=content,
                    metadata={"heading": heading_text},
                )
            )

        return docs

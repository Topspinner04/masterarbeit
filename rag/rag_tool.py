class RAGTool:
    def __init__(self, retriever):
        self.retriever = retriever

    def perform_rag_search(self, query: str) -> str:
        """Performs a RAG search for the given query in the architecture documentation and returns the top 3 results.
        :param query: The search query string.
        :return: The top three answers from the RAG search, formatted as a single string with source headings.
        """
        docs = self.retriever.retrieve(query)

        context = "\n\n".join(
            f"[Source {i + 1} (Characters {doc.metadata['start_char']} - {doc.metadata['end_char']})]\n{doc.content}"
            for i, doc in enumerate(docs)
        )

        return context

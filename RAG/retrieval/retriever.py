from __future__ import annotations

from RAG.retrieval.faiss_store import (
    FAISSStore,
    SearchResult,
)


class Retriever:
    """
    Semantic retriever connecting the embedding model
    with the FAISS vector store.

    Pipeline:

        Text Chunks
            ↓
        EmbeddingModel
            ↓
        FAISSStore
            ↓
        Top-K Search Results
    """

    def __init__(
        self,
        embedding_model,
    ) -> None:

        self.embedding_model = (
            embedding_model
        )

        self.store = FAISSStore(
            dimension=embedding_model.dimension
        )

    def index_chunks(
        self,
        chunks: list,
    ) -> None:
        """
        Generate embeddings for document chunks
        and add them to the FAISS index.
        """

        if not chunks:
            raise ValueError(
                "Cannot index an empty chunk list."
            )

        texts = [
            self._get_chunk_text(
                chunk
            )
            for chunk in chunks
        ]

        embedding_result = (
            self.embedding_model.encode(
                texts
            )
        )

        self.store.add(
            embedding_result.embeddings,
            chunks,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Convert a user query into an embedding
        and search the FAISS index.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query_embedding = (
            self.embedding_model.encode_query(
                query
            )
        )

        return self.store.search(
            query_embedding,
            top_k=top_k,
        )

    def size(self) -> int:
        """
        Return the number of indexed chunks.
        """

        return self.store.size()

    def _get_chunk_text(
        self,
        chunk,
    ) -> str:
        """
        Extract text from a chunk.

        The current chunk generator should expose
        chunk.text.
        """

        text = getattr(
            chunk,
            "text",
            None,
        )

        if text is None:
            raise ValueError(
                "Chunk does not contain a text field."
            )

        text = str(text).strip()

        if not text:
            raise ValueError(
                "Chunk contains empty text."
            )

        return text
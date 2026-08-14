from __future__ import annotations

from dataclasses import dataclass

import faiss
import numpy as np


@dataclass
class SearchResult:
    """
    Represents a single FAISS retrieval result.
    """

    chunk_id: str
    score: float
    text: str
    section: str | None
    page_start: int | None
    page_end: int | None


class FAISSStore:
    """
    FAISS-based vector store for semantic retrieval.

    The store keeps:
        - FAISS vector index
        - chunk metadata

    Vectors are normalized and searched using
    inner-product similarity, which is equivalent
    to cosine similarity for normalized embeddings.
    """

    def __init__(
        self,
        dimension: int,
    ) -> None:

        if dimension <= 0:
            raise ValueError(
                "Embedding dimension must be positive."
            )

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.chunks: list = []

    def add(
        self,
        embeddings: np.ndarray,
        chunks: list,
    ) -> None:
        """
        Add chunk embeddings and their corresponding
        chunk objects to the FAISS index.
        """

        if len(embeddings) == 0:
            return

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings must match "
                "number of chunks."
            )

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension "
                f"{self.dimension}, got "
                f"{vectors.shape[1]}."
            )

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Search for the most semantically similar chunks.
        """

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if self.index.ntotal == 0:
            return []

        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.ndim != 2:
            raise ValueError(
                "Query embedding must be a 1D "
                "or 2D array."
            )

        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Expected query dimension "
                f"{self.dimension}, got "
                f"{query.shape[1]}."
            )

        faiss.normalize_L2(query)

        actual_k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query,
            actual_k,
        )

        results: list[SearchResult] = []

        for score, index_id in zip(
            scores[0],
            indices[0],
        ):

            if index_id < 0:
                continue

            chunk = self.chunks[index_id]

            results.append(
                SearchResult(
                    chunk_id=self._get_chunk_id(
                        chunk,
                        index_id,
                    ),
                    score=float(score),
                    text=self._get_chunk_text(
                        chunk
                    ),
                    section=self._get_chunk_section(
                        chunk
                    ),
                    page_start=self._get_page_start(
                        chunk
                    ),
                    page_end=self._get_page_end(
                        chunk
                    ),
                )
            )

        return results

    def size(self) -> int:
        """
        Return the number of vectors currently stored.
        """

        return self.index.ntotal

    def _get_chunk_id(
        self,
        chunk,
        index_id: int,
    ) -> str:

        return str(
            getattr(
                chunk,
                "chunk_id",
                f"chunk_{index_id:05d}",
            )
        )

    def _get_chunk_text(
        self,
        chunk,
    ) -> str:

        return str(
            getattr(
                chunk,
                "text",
                "",
            )
        )

    def _get_chunk_section(
        self,
        chunk,
    ) -> str | None:

        section = getattr(
            chunk,
            "section",
            None,
        )

        if section is None:
            return None

        if hasattr(section, "title"):
            return str(section.title)

        return str(section)

    def _get_page_start(
        self,
        chunk,
    ) -> int | None:

        value = getattr(
            chunk,
            "page_start",
            None,
        )

        if value is not None:
            return int(value)

        pages = getattr(
            chunk,
            "pages",
            None,
        )

        if pages:
            return int(min(pages))

        return None

    def _get_page_end(
        self,
        chunk,
    ) -> int | None:

        value = getattr(
            chunk,
            "page_end",
            None,
        )

        if value is not None:
            return int(value)

        pages = getattr(
            chunk,
            "pages",
            None,
        )

        if pages:
            return int(max(pages))

        return None
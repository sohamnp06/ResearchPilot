from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbeddingResult:
    """
    Stores embeddings generated for a collection of texts.
    """

    texts: list[str]
    embeddings: np.ndarray


class EmbeddingModel:
    """
    Wrapper around the Sentence Transformers embedding model.

    The model is loaded once and reused for multiple
    embedding operations.
    """

    MODEL_NAME = (
        "sentence-transformers/"
        "static-retrieval-mrl-en-v1"
    )

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ) -> None:

        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

    def encode(
        self,
        texts: list[str],
        batch_size: int = 32,
        normalize_embeddings: bool = True,
    ) -> EmbeddingResult:

        if not texts:
            return EmbeddingResult(
                texts=[],
                embeddings=np.empty(
                    (0, 0),
                    dtype=np.float32,
                ),
            )

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=(
                normalize_embeddings
            ),
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        return EmbeddingResult(
            texts=texts,
            embeddings=embeddings,
        )

    def encode_query(
        self,
        query: str,
    ) -> np.ndarray:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return np.asarray(
            embedding,
            dtype=np.float32,
        )

    @property
    def dimension(self) -> int:

        return self.model.get_embedding_dimension()
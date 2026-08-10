from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from RAG.chunking.models import Sentence, SemanticChunk
from RAG.embedding.embed import EmbeddingModel


@dataclass
class SimilarityScore:
    """
    Represents semantic similarity between two
    consecutive sentences.
    """

    left_index: int
    right_index: int
    score: float


class SemanticChunker:
    """
    Creates semantically coherent chunks from sentences.

    The chunker:

    1. Embeds sentences.
    2. Calculates similarity between adjacent sentences.
    3. Detects significant similarity drops.
    4. Respects section boundaries.
    5. Respects maximum chunk size.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        max_characters: int = 3000,
        min_sentences: int = 2,
        similarity_percentile: float = 20.0,
    ) -> None:

        if max_characters <= 0:
            raise ValueError(
                "max_characters must be greater than 0."
            )

        if min_sentences <= 0:
            raise ValueError(
                "min_sentences must be greater than 0."
            )

        if not 0 < similarity_percentile < 100:
            raise ValueError(
                "similarity_percentile must be "
                "between 0 and 100."
            )

        self.embedding_model = embedding_model
        self.max_characters = max_characters
        self.min_sentences = min_sentences
        self.similarity_percentile = (
            similarity_percentile
        )

    def chunk(
        self,
        sentences: list[Sentence],
    ) -> list[SemanticChunk]:

        if not sentences:
            return []

        chunks: list[SemanticChunk] = []

        # Process each section independently.
        sections = self._group_by_section(
            sentences
        )

        chunk_counter = 0

        for section_sentences in sections:

            section_chunks = (
                self._chunk_section(
                    section_sentences
                )
            )

            for chunk in section_chunks:

                chunk.chunk_id = (
                    f"chunk_{chunk_counter:05d}"
                )

                chunks.append(chunk)

                chunk_counter += 1

        return chunks

    def _group_by_section(
        self,
        sentences: list[Sentence],
    ) -> list[list[Sentence]]:

        groups: list[list[Sentence]] = []

        current_group: list[Sentence] = []

        current_section = None

        for sentence in sentences:

            if (
                current_group
                and sentence.section
                != current_section
            ):

                groups.append(
                    current_group
                )

                current_group = []

            current_group.append(
                sentence
            )

            current_section = (
                sentence.section
            )

        if current_group:
            groups.append(
                current_group
            )

        return groups

    def _chunk_section(
        self,
        sentences: list[Sentence],
    ) -> list[SemanticChunk]:

        if not sentences:
            return []

        if len(sentences) <= 1:

            return [
                self._build_chunk(
                    sentences
                )
            ]

        texts = [
            sentence.text
            for sentence in sentences
        ]

        embedding_result = (
            self.embedding_model.encode(
                texts
            )
        )

        embeddings = (
            embedding_result.embeddings
        )

        similarities = (
            self._calculate_similarities(
                embeddings
            )
        )

        boundaries = (
            self._detect_boundaries(
                similarities,
                len(sentences),
            )
        )

        return self._build_chunks_from_boundaries(
            sentences,
            boundaries,
        )

    def _calculate_similarities(
        self,
        embeddings: np.ndarray,
    ) -> list[SimilarityScore]:

        if len(embeddings) < 2:
            return []

        similarities: list[
            SimilarityScore
        ] = []

        for index in range(
            len(embeddings) - 1
        ):

            left = embeddings[index]
            right = embeddings[index + 1]

            score = float(
                np.dot(left, right)
            )

            similarities.append(
                SimilarityScore(
                    left_index=index,
                    right_index=index + 1,
                    score=score,
                )
            )

        return similarities

    def _detect_boundaries(
        self,
        similarities: list[SimilarityScore],
        sentence_count: int,
    ) -> set[int]:

        if not similarities:
            return set()

        scores = np.array(
            [
                item.score
                for item in similarities
            ],
            dtype=np.float32,
        )

        threshold = float(
            np.percentile(
                scores,
                self.similarity_percentile,
            )
        )

        boundaries: set[int] = set()

        for item in similarities:

            if item.score <= threshold:

                boundaries.add(
                    item.right_index
                )

        return boundaries

    def _build_chunks_from_boundaries(
        self,
        sentences: list[Sentence],
        boundaries: set[int],
    ) -> list[SemanticChunk]:

        chunks: list[SemanticChunk] = []

        current: list[Sentence] = []

        for index, sentence in enumerate(
            sentences
        ):

            if (
                current
                and index in boundaries
                and len(current)
                >= self.min_sentences
            ):

                chunks.append(
                    self._build_chunk(
                        current
                    )
                )

                current = []

            proposed = (
                current + [sentence]
            )

            proposed_text = self._join_text(
                proposed
            )

            if (
                current
                and len(proposed_text)
                > self.max_characters
            ):

                chunks.append(
                    self._build_chunk(
                        current
                    )
                )

                current = []

            current.append(
                sentence
            )

        if current:

            chunks.append(
                self._build_chunk(
                    current
                )
            )

        return chunks

    def _build_chunk(
        self,
        sentences: list[Sentence],
    ) -> SemanticChunk:

        text = self._join_text(
            sentences
        )

        first = sentences[0]
        last = sentences[-1]

        bboxes = [
            sentence.bbox
            for sentence in sentences
            if sentence.bbox is not None
        ]

        return SemanticChunk(
            chunk_id="pending",
            text=text,
            page_start=first.page,
            page_end=last.page,
            section=first.section,
            heading=first.heading,
            sentence_start=(
                first.sentence_index
            ),
            sentence_end=(
                last.sentence_index
            ),
            bboxes=bboxes,
            sentence_count=len(sentences),
            character_count=len(text),
        )

    def _join_text(
        self,
        sentences: list[Sentence],
    ) -> str:

        return " ".join(
            sentence.text.strip()
            for sentence in sentences
        )
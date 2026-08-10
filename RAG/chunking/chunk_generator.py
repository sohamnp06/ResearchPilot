from RAG.chunking.models import Sentence, SemanticChunk


class ChunkGenerator:
    """
    Generates initial chunks from consecutive sentences.

    This component does not perform semantic similarity.
    It provides a controlled chunking layer that respects
    section boundaries and maximum size constraints.
    """

    def __init__(
        self,
        max_characters: int = 3000,
    ) -> None:

        if max_characters <= 0:
            raise ValueError(
                "max_characters must be greater than 0"
            )

        self.max_characters = max_characters

    def generate(
        self,
        sentences: list[Sentence],
    ) -> list[SemanticChunk]:

        if not sentences:
            return []

        chunks: list[SemanticChunk] = []

        current_sentences: list[Sentence] = []

        for sentence in sentences:

            if not sentence.text.strip():
                continue

            # Start a new chunk when the section changes.
            if (
                current_sentences
                and self._section_changed(
                    current_sentences[-1],
                    sentence,
                )
            ):

                chunks.append(
                    self._build_chunk(
                        current_sentences,
                        len(chunks),
                    )
                )

                current_sentences = []

            # Check maximum character limit.
            proposed_text = self._join_text(
                current_sentences
                + [sentence]
            )

            if (
                current_sentences
                and len(proposed_text)
                > self.max_characters
            ):

                chunks.append(
                    self._build_chunk(
                        current_sentences,
                        len(chunks),
                    )
                )

                current_sentences = []

            current_sentences.append(
                sentence
            )

        if current_sentences:

            chunks.append(
                self._build_chunk(
                    current_sentences,
                    len(chunks),
                )
            )

        return chunks

    def _section_changed(
        self,
        previous: Sentence,
        current: Sentence,
    ) -> bool:

        return (
            previous.section
            != current.section
        )

    def _join_text(
        self,
        sentences: list[Sentence],
    ) -> str:

        return " ".join(
            sentence.text.strip()
            for sentence in sentences
        )

    def _build_chunk(
        self,
        sentences: list[Sentence],
        chunk_number: int,
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
            chunk_id=f"chunk_{chunk_number:05d}",
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
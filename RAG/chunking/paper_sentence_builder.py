from RAG.chunking.models import Sentence
from RAG.chunking.sentence_splitter import SentenceSplitter


class PaperSentenceBuilder:
    """
    Converts structured document sections into sentences
    while preserving section and heading metadata.
    """

    def __init__(
        self,
        sentence_splitter: SentenceSplitter,
    ) -> None:

        self.sentence_splitter = (
            sentence_splitter
        )

    def build(
        self,
        sections,
    ) -> list[Sentence]:

        sentences: list[Sentence] = []

        sentence_index = 0

        for section in sections:

            for block in section.blocks:

                block_sentences = (
                    self.sentence_splitter.split_block(
                        text=block.text,
                        page=block.page,
                        block_number=block.block_number,
                        bbox=block.bbox,
                        section=section.title,
                        heading=section.title,
                        starting_index=sentence_index,
                    )
                )

                sentences.extend(
                    block_sentences
                )

                sentence_index += len(
                    block_sentences
                )

        return sentences
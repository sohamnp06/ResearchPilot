from RAG.chunking.models import Sentence
from RAG.pdf_pipeline.models import PageContent


class SentenceSplitter:
    """
    Splits structured PDF blocks into sentences while
    preserving document metadata.
    """

    def __init__(self) -> None:

        import spacy

        self.nlp = spacy.blank("en")

        self.nlp.add_pipe(
            "sentencizer"
        )

    def split(
        self,
        pages: list[PageContent],
    ) -> list[Sentence]:
        """Split all extracted PDF text blocks into ordered sentences.

        The RAG pipeline operates on a complete document, whereas
        :meth:`split_block` is also used by the document-structure pipeline.
        Keeping the document-level operation here ensures both paths produce
        the same sentence objects and preserves their source metadata.
        """
        sentences: list[Sentence] = []
        sentence_index = 0

        for page in pages:
            for block in page.blocks:
                block_sentences = self.split_block(
                    text=block.text,
                    page=page.page_number,
                    block_number=block.block_number,
                    bbox=block.bbox,
                    starting_index=sentence_index,
                )
                sentences.extend(block_sentences)
                sentence_index += len(block_sentences)

        return sentences

    def split_block(
        self,
        text: str,
        page: int,
        block_number: int,
        bbox: tuple[
            float,
            float,
            float,
            float,
        ] | None = None,
        section: str | None = None,
        heading: str | None = None,
        starting_index: int = 0,
    ) -> list[Sentence]:

        text = text.strip()

        if not text:
            return []

        doc = self.nlp(text)

        sentences: list[Sentence] = []

        for offset, sent in enumerate(
            doc.sents
        ):

            sentence_text = sent.text.strip()

            if not sentence_text:
                continue

            sentences.append(
                Sentence(
                    text=sentence_text,
                    page=page,
                    block_number=block_number,
                    sentence_index=(
                        starting_index + offset
                    ),
                    section=section,
                    heading=heading,
                    bbox=bbox,
                )
            )

        return sentences

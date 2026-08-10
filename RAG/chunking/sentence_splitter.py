from RAG.chunking.models import Sentence


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
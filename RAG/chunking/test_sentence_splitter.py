from pathlib import Path

from RAG.chunking.sentence_splitter import (
    SentenceSplitter,
)
from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:

    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(
        pdf_path
    )

    splitter = SentenceSplitter()

    total_sentences = 0

    for page in pages:

        for block in page.blocks:

            sentences = splitter.split_block(
                text=block.text,
                page=page.page_number,
                block_number=block.block_number,
                bbox=block.bbox,
            )

            for sentence in sentences:

                print(
                    f"[Sentence "
                    f"{sentence.sentence_index}] "
                    f"Page={sentence.page} "
                    f"Block={sentence.block_number}"
                )

                print(
                    sentence.text
                )

                print()

                total_sentences += 1

    print(
        f"Total sentences: "
        f"{total_sentences}"
    )


if __name__ == "__main__":
    main()
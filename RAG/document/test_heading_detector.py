from pathlib import Path

from RAG.document.heading_detector import HeadingDetector
from RAG.pdf_pipeline.extractor import PDFExtractor


def main() -> None:
    pdf_path = Path(
        "data/papers/2105.02723v1.pdf"
    )

    extractor = PDFExtractor()

    pages = extractor.extract(pdf_path)

    detector = HeadingDetector()

    for page in pages:

        for block in page.blocks:

            score = detector.score(
                block,
                page.blocks,
            )

            if detector.is_heading(
                block,
                page.blocks,
            ):
                print(
                    f"[HEADING] "
                    f"Page={page.page_number} "
                    f"Score={score:.2f} "
                    f"Text={block.text}"
                )


if __name__ == "__main__":
    main()
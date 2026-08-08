from pathlib import Path

import pymupdf

from RAG.pdf_pipeline.models import (
    PageContent,
    TextBlock,
    TextSpan,
)


class PDFExtractor:
    """
    Extracts structured text and layout information
    from PDF documents using PyMuPDF.
    """

    def extract(self, pdf_path: Path) -> list[PageContent]:
        """
        Extract pages, blocks, lines, and spans from a PDF.

        Layout information such as bounding boxes, fonts,
        and font sizes is preserved for downstream
        document-structure analysis.
        """

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        document = pymupdf.open(pdf_path)

        pages: list[PageContent] = []

        try:
            for page_number, page in enumerate(
                document,
                start=1,
            ):
                page_data = page.get_text("dict")

                blocks: list[TextBlock] = []

                for block_number, block in enumerate(
                    page_data.get("blocks", [])
                ):
                    if block.get("type") != 0:
                        continue

                    spans: list[TextSpan] = []

                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get(
                                "text",
                                "",
                            ).strip()

                            if not text:
                                continue

                            spans.append(
                                TextSpan(
                                    text=text,
                                    bbox=tuple(
                                        span["bbox"]
                                    ),
                                    font=span.get("font"),
                                    font_size=span.get(
                                        "size"
                                    ),
                                    flags=span.get("flags"),
                                )
                            )

                    if not spans:
                        continue

                    block_text = " ".join(
                        span.text
                        for span in spans
                    )

                    blocks.append(
                        TextBlock(
                            page=page_number,
                            block_number=block_number,
                            bbox=tuple(
                                block["bbox"]
                            ),
                            text=block_text,
                            spans=spans,
                        )
                    )

                pages.append(
                    PageContent(
                        page_number=page_number,
                        width=page.rect.width,
                        height=page.rect.height,
                        blocks=blocks,
                    )
                )

        finally:
            document.close()

        return pages
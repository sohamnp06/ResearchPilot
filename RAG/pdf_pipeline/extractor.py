from pathlib import Path
import pymupdf


class PDFExtractor:
    """
    Extracts low-level text blocks and layout information
    from PDF documents using PyMuPDF.
    """

    def extract(self, pdf_path: Path) -> list[dict]:
        """
        Extract text blocks from every page of a PDF.

        Each block contains text, page information,
        and bounding-box coordinates.
        """

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        document = pymupdf.open(pdf_path)

        blocks: list[dict] = []

        try:
            for page_number, page in enumerate(
                document,
                start=1,
            ):
                page_blocks = page.get_text(
                    "dict"
                ).get("blocks", [])

                for block_number, block in enumerate(
                    page_blocks
                ):
                    if block.get("type") != 0:
                        continue

                    lines = block.get(
                        "lines",
                        [],
                    )

                    for line in lines:
                        spans = line.get(
                            "spans",
                            [],
                        )

                        for span in spans:
                            text = span.get(
                                "text",
                                "",
                            ).strip()

                            if not text:
                                continue

                            blocks.append(
                                {
                                    "page": page_number,
                                    "block": block_number,
                                    "text": text,
                                    "bbox": block.get(
                                        "bbox"
                                    ),
                                    "font": span.get(
                                        "font"
                                    ),
                                    "font_size": span.get(
                                        "size"
                                    ),
                                    "flags": span.get(
                                        "flags"
                                    ),
                                }
                            )

        finally:
            document.close()

        return blocks
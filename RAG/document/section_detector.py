import re
from dataclasses import dataclass

from RAG.pdf_pipeline.models import TextBlock


@dataclass
class DetectedSection:
    """
    Represents a detected section in a research paper.
    """

    title: str
    level: int
    page: int
    block_number: int
    blocks: list[TextBlock]


class SectionDetector:
    """
    Detects hierarchical sections while excluding
    document metadata such as title blocks.
    """

    NUMBERING_PATTERN = re.compile(
        r"^\s*(\d+(?:\.\d+)*)[\.\)]?\s+"
    )

    def detect(
        self,
        pages: list,
        heading_detector,
        metadata=None,
    ) -> list[DetectedSection]:

        sections: list[DetectedSection] = []

        current_section: (
            DetectedSection | None
        ) = None

        metadata_block_numbers = (
            self._get_metadata_block_numbers(
                metadata
            )
        )

        for page in pages:

            for block in page.blocks:

                # -----------------------------------------
                # Ignore title metadata blocks.
                #
                # Metadata block numbers are only meaningful
                # for the first page.
                # -----------------------------------------

                if (
                    page.page_number == 1
                    and block.block_number
                    in metadata_block_numbers
                ):
                    continue

                # -----------------------------------------
                # Heading detection
                # -----------------------------------------

                if heading_detector.is_heading(
                    block,
                    page.blocks,
                ):

                    # Save previous section.
                    if current_section is not None:
                        sections.append(
                            current_section
                        )

                    level = self._detect_level(
                        block.text
                    )

                    current_section = (
                        DetectedSection(
                            title=block.text.strip(),
                            level=level,
                            page=page.page_number,
                            block_number=block.block_number,
                            blocks=[],
                        )
                    )

                # -----------------------------------------
                # Normal body content
                # -----------------------------------------

                elif current_section is not None:

                    current_section.blocks.append(
                        block
                    )

        # Save final section.
        if current_section is not None:
            sections.append(
                current_section
            )

        return sections

    # ==================================================
    # METADATA BLOCKS
    # ==================================================

    def _get_metadata_block_numbers(
        self,
        metadata,
    ) -> set[int]:

        if metadata is None:
            return set()

        return metadata.title_block_numbers

    # ==================================================
    # SECTION LEVEL
    # ==================================================

    def _detect_level(
        self,
        heading: str,
    ) -> int:

        match = self.NUMBERING_PATTERN.match(
            heading
        )

        # Unnumbered headings such as:
        #
        # Abstract
        # References
        #
        # are treated as top-level.
        if not match:
            return 1

        numbering = match.group(1)

        return numbering.count(".") + 1
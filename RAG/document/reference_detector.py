import re
from dataclasses import dataclass

from RAG.pdf_pipeline.models import TextBlock


@dataclass
class Reference:
    """
    Represents a single bibliographic reference.
    """

    index: int | None
    text: str
    page: int
    block_number: int


class ReferenceDetector:
    """
    Detects the reference section and separates
    individual references even when multiple references
    exist inside the same PDF text block.
    """

    REFERENCE_HEADING_PATTERN = re.compile(
        r"^\s*(references|bibliography)\s*$",
        re.IGNORECASE,
    )

    # This paper uses square-bracket reference numbering:
    #
    # [1]
    # [2]
    # [3]
    #
    # We intentionally do NOT accept:
    #
    # 2021.
    # 2009.
    #
    # because those are publication years, not references.
    REFERENCE_START_PATTERN = re.compile(
        r"\[\s*(\d{1,3})\s*\]"
    )

    def detect(
        self,
        pages: list,
    ) -> list[Reference]:

        reference_blocks: list[TextBlock] = []

        inside_references = False

        for page in pages:

            for block in page.blocks:

                text = block.text.strip()

                # Detect the beginning of the
                # References section.
                if self._is_reference_heading(
                    text
                ):
                    inside_references = True
                    continue

                # Ignore everything before
                # the References section.
                if not inside_references:
                    continue

                reference_blocks.append(
                    block
                )

        return self._build_references(
            reference_blocks
        )

    def _is_reference_heading(
        self,
        text: str,
    ) -> bool:

        return bool(
            self.REFERENCE_HEADING_PATTERN.match(
                text
            )
        )

    def _build_references(
        self,
        blocks: list[TextBlock],
    ) -> list[Reference]:

        references: list[Reference] = []

        for block in blocks:

            text = block.text.strip()

            # Find all reference markers inside
            # the current PDF block.
            #
            # Example:
            #
            # [1] Author...
            # [2] Author...
            # [3] Author...
            #
            matches = list(
                self.REFERENCE_START_PATTERN.finditer(
                    text
                )
            )

            if not matches:
                continue

            for position, match in enumerate(
                matches
            ):

                # Start of this reference.
                start = match.start()

                # End of this reference is the
                # beginning of the next reference.
                if position + 1 < len(matches):

                    end = matches[
                        position + 1
                    ].start()

                else:

                    end = len(text)

                reference_text = text[
                    start:end
                ].strip()

                index = int(
                    match.group(1)
                )

                references.append(
                    Reference(
                        index=index,
                        text=reference_text,
                        page=block.page,
                        block_number=block.block_number,
                    )
                )

        return references
from __future__ import annotations

from RAG.document.elements import (
    DocumentElement,
    ElementType,
)


class SectionAssigner:
    """
    Assigns the correct section and heading to each
    document element based on the detected sections.
    """

    def assign(
        self,
        elements: list[DocumentElement],
        sections: list,
    ) -> list[DocumentElement]:

        if not elements or not sections:
            return elements

        for element in elements:

            section = self._find_section(
                element,
                sections,
            )

            if section is None:
                continue

            element.section = section.title
            element.heading = section.title

        return elements

    def _find_section(
        self,
        element: DocumentElement,
        sections: list,
    ):

        candidates = []

        for section in sections:

            if section.page > element.page:
                continue

            if (
                section.page == element.page
                and section.block_number
                > element.block_number
            ):
                continue

            candidates.append(section)

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda section: (
                section.page,
                section.block_number,
            ),
        )
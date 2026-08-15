from __future__ import annotations

from dataclasses import dataclass

from RAG.retrieval.faiss_store import SearchResult


@dataclass
class ContextItem:
    """
    Represents one retrieved piece of context.

    This keeps the original retrieval metadata so
    the eventual LLM response can be traced back
    to the source chunk.
    """

    chunk_id: str
    score: float
    section: str | None
    page_start: int | None
    page_end: int | None
    text: str


@dataclass
class AssembledContext:
    """
    Represents the complete context supplied to
    the generation layer.
    """

    query: str
    items: list[ContextItem]
    text: str


class ContextAssembler:
    """
    Converts FAISS SearchResults into structured,
    LLM-ready context.

    Responsibilities:

        SearchResult
            ↓
        ContextItem
            ↓
        Formatted context

    This component does NOT call an LLM.
    """

    def __init__(
        self,
        max_context_characters: int = 12000,
    ) -> None:

        if max_context_characters <= 0:
            raise ValueError(
                "max_context_characters must "
                "be greater than zero."
            )

        self.max_context_characters = (
            max_context_characters
        )

    def assemble(
        self,
        query: str,
        results: list[SearchResult],
    ) -> AssembledContext:
        """
        Assemble retrieved results into LLM-ready
        context.

        Results are kept in their retrieval order.
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not results:
            return AssembledContext(
                query=query,
                items=[],
                text="",
            )

        items: list[ContextItem] = []

        current_length = 0

        for result in results:

            text = result.text.strip()

            if not text:
                continue

            item = ContextItem(
                chunk_id=result.chunk_id,
                score=result.score,
                section=result.section,
                page_start=result.page_start,
                page_end=result.page_end,
                text=text,
            )

            formatted = self._format_item(
                item
            )

            additional_length = len(
                formatted
            )

            if (
                current_length
                + additional_length
                > self.max_context_characters
            ):
                break

            items.append(
                item
            )

            current_length += (
                additional_length
            )

        context_text = self._build_context_text(
            items
        )

        return AssembledContext(
            query=query,
            items=items,
            text=context_text,
        )

    def _format_item(
        self,
        item: ContextItem,
    ) -> str:
        """
        Format one context item with source
        metadata.
        """

        section = (
            item.section
            if item.section
            else "Unknown"
        )

        if (
            item.page_start is not None
            and item.page_end is not None
        ):

            if (
                item.page_start
                == item.page_end
            ):
                pages = str(
                    item.page_start
                )

            else:
                pages = (
                    f"{item.page_start}-"
                    f"{item.page_end}"
                )

        else:
            pages = "Unknown"

        return (
            f"[Source: {item.chunk_id} | "
            f"Section: {section} | "
            f"Pages: {pages} | "
            f"Score: {item.score:.4f}]\n"
            f"{item.text}\n\n"
        )

    def _build_context_text(
        self,
        items: list[ContextItem],
    ) -> str:
        """
        Combine all context items into one string.
        """

        if not items:
            return ""

        return "".join(
            self._format_item(item)
            for item in items
        ).strip()
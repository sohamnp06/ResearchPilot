from pathlib import Path

import httpx

from RAG.paper_search.cache import PaperCache
from RAG.paper_search.exceptions import ProviderError
from RAG.paper_search.models import Paper


class PaperDownloader:
    """
    Downloads research-paper PDFs and stores them in the local cache.
    """

    def __init__(
        self,
        cache: PaperCache,
    ) -> None:
        self._cache = cache

    async def download(self, paper: Paper) -> Path:
        """
        Download a paper PDF and return its local path.

        If the paper is already cached, no network request is made.
        """

        if not paper.pdf_url:
            raise ProviderError(
                message=(
                    f"No PDF URL available for paper "
                    f"'{paper.title}'."
                ),
                provider=paper.source,
            )

        cached_path = self._cache.get_path(
            paper.paper_id
        )

        if cached_path.is_file():
            return cached_path

        try:
            async with httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
            ) as client:

                response = await client.get(
                    str(paper.pdf_url)
                )

        except httpx.RequestError as exc:
            raise ProviderError(
                message=(
                    f"Failed to download PDF for "
                    f"'{paper.title}': {exc}"
                ),
                provider=paper.source,
            ) from exc

        if response.status_code != 200:
            raise ProviderError(
                message=(
                    f"PDF download failed with "
                    f"HTTP {response.status_code}."
                ),
                provider=paper.source,
                status_code=response.status_code,
            )

        content_type = response.headers.get(
            "content-type",
            ""
        ).lower()

        if (
            "application/pdf" not in content_type
            and not response.content.startswith(b"%PDF")
        ):
            raise ProviderError(
                message=(
                    f"Downloaded content for "
                    f"'{paper.title}' does not appear "
                    "to be a valid PDF."
                ),
                provider=paper.source,
            )

        self._write_pdf_atomically(
            cached_path,
            response.content,
        )

        return cached_path

    def _write_pdf_atomically(
        self,
        destination: Path,
        content: bytes,
    ) -> None:
        """
        Write the PDF using a temporary file first.

        This prevents partially downloaded files from
        being mistaken for valid cached PDFs.
        """

        temporary_path = destination.with_suffix(
            ".tmp"
        )

        try:
            temporary_path.write_bytes(content)
            temporary_path.replace(destination)

        finally:
            if temporary_path.exists():
                temporary_path.unlink()
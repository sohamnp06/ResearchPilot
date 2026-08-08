from typing import Sequence

from RAG.paper_search.exceptions import ProviderError
from RAG.paper_search.models import Paper
from RAG.paper_search.providers.base_provider import BaseProvider


class PaperSearchService:
    """
    Orchestrates searches across configured paper providers.
    """

    def __init__(
        self,
        providers: Sequence[BaseProvider],
    ) -> None:

        if not providers:
            raise ValueError(
                "At least one paper search provider is required."
            )

        self._providers = list(providers)

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Paper]:

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError(
                "Search query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Search limit must be greater than zero."
            )

        provider_errors: list[ProviderError] = []

        for provider in self._providers:

            try:
                results = await provider.search(
                    query=normalized_query,
                    limit=limit,
                )

                if results:
                    return results

            except ProviderError as exc:
                provider_errors.append(exc)
                continue

        if provider_errors:
            first_error = provider_errors[0]

            raise ProviderError(
                message=(
                    "All configured paper search providers "
                    "failed. "
                    f"First failure: {first_error}"
                ),
                provider=first_error.provider,
                status_code=first_error.status_code,
            )

        return []
class PaperSearchError(Exception):
    """Base exception for paper search operations."""


class PaperNotFoundError(PaperSearchError):
    """Raised when no papers are found."""


class ProviderError(PaperSearchError):
    """Raised when a paper provider fails."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)

        self.provider = provider
        self.status_code = status_code
class PaperSearchError(Exception):
    """Base exception for paper search."""


class PaperNotFoundError(PaperSearchError):
    """Raised when no papers are found."""


class ProviderError(PaperSearchError):
    """Raised when provider request fails."""
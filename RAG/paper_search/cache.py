from pathlib import Path

from RAG.settings import settings


class PaperCache:
    """
    Manages locally cached research-paper PDFs.
    """

    def __init__(self) -> None:
        self.paper_directory = Path(settings.PAPER_DIR)

        self.paper_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_path(self, paper_id: str) -> Path:
        """
        Return the expected local path for a paper.
        """

        safe_paper_id = self._sanitize_paper_id(paper_id)

        return self.paper_directory / f"{safe_paper_id}.pdf"

    def exists(self, paper_id: str) -> bool:
        """
        Check whether a paper is already cached.
        """

        return self.get_path(paper_id).is_file()

    def _sanitize_paper_id(self, paper_id: str) -> str:
        """
        Convert a provider-specific paper ID into a safe filename.
        """

        return "".join(
            character
            if character.isalnum() or character in "-_."
            else "_"
            for character in paper_id
        )
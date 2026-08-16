"""
RAGClient — The integration bridge between the FastAPI backend and the RAG pipeline.

Architecture:
    Backend Route
        ↓
    RAGClient (singleton)
        ↓
    ┌──────────────────┐    ┌───────────────────┐
    │  EmbeddingModel  │    │  LLMGenerator     │
    │  (loaded once)   │    │  (Ollama/OpenAI)  │
    └──────────────────┘    └───────────────────┘
        ↓                          ↓
    Per-document Retriever    ContextAssembler
        ↓                          ↓
    FAISSStore             PaperSummarizer / InformationExtractor /
    (keyed by paper_id)    ResearchGapDetector / CitationVerifier /
                           PaperComparator
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from RAG.embedding.embed import EmbeddingModel
from RAG.retrieval.retriever import Retriever
from RAG.generation.llm_generator import LLMGenerator
from RAG.generation.context_assembler import ContextAssembler
from RAG.generation.summarizer import PaperSummarizer
from RAG.generation.information_extractor import InformationExtractor
from RAG.generation.research_gap_detector import ResearchGapDetector
from RAG.generation.citation_verifier import CitationVerifier
from RAG.generation.paper_comparator import PaperComparator
from RAG.pdf_pipeline.extractor import PDFExtractor
from RAG.chunking.sentence_splitter import SentenceSplitter
from RAG.chunking.chunk_generator import ChunkGenerator

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _get_settings():
    """Import settings lazily to avoid circular imports."""
    from backend.app.core.config import settings
    return settings


# ──────────────────────────────────────────────────────────────────────────────
# RAG CLIENT
# ──────────────────────────────────────────────────────────────────────────────

class RAGClient:
    """
    Singleton RAG client used by all backend routes.

    Manages:
    - A single shared EmbeddingModel (loaded once at startup)
    - A single shared LLMGenerator
    - Per-document Retriever instances (keyed by paper_id)
    - Full PDF → chunks → embeddings → FAISS pipeline
    """

    _instance: Optional["RAGClient"] = None

    def __init__(self) -> None:
        self._embedding_model: Optional[EmbeddingModel] = None
        self._llm_generator: Optional[LLMGenerator] = None
        self._retrievers: dict[str, Retriever] = {}
        self._initialized = False
        self._settings = _get_settings()
        self._faiss_root = Path(self._settings.FAISS_STORAGE_PATH)
        self._faiss_root.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "RAGClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ──────────────────────────────────────────────────────────
    # INITIALIZATION
    # ──────────────────────────────────────────────────────────

    def initialize(self) -> None:
        """
        Load the embedding model and LLM generator.
        Called once at backend startup.
        """
        if self._initialized:
            return

        logger.info("Loading embedding model (static-retrieval-mrl-en-v1)...")
        self._embedding_model = EmbeddingModel()
        logger.info(f"Embedding model loaded — dimension: {self._embedding_model.dimension}")

        settings = self._settings
        logger.info(
            f"Initializing LLM generator — provider={settings.LLM_PROVIDER}, "
            f"model={settings.OLLAMA_MODEL}"
        )
        self._llm_generator = LLMGenerator(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        logger.info("LLM generator ready.")

        # Re-load any existing FAISS indexes from disk
        self._load_existing_indexes()

        self._initialized = True
        logger.info("RAGClient initialization complete.")

    def _load_existing_indexes(self) -> None:
        """
        Load any previously saved FAISS indexes from disk.
        """
        if not self._faiss_root.exists():
            return

        for paper_dir in self._faiss_root.iterdir():
            if not paper_dir.is_dir():
                continue
            index_file = paper_dir / "index.faiss"
            chunks_file = paper_dir / "chunks.npz"
            if index_file.exists() and chunks_file.exists():
                paper_id = paper_dir.name
                try:
                    retriever = self._make_retriever()
                    retriever.load(paper_dir)
                    self._retrievers[paper_id] = retriever
                    logger.info(f"Loaded FAISS index for paper: {paper_id}")
                except Exception as exc:
                    logger.warning(f"Could not load FAISS index for {paper_id}: {exc}")

    def _make_retriever(self) -> Retriever:
        if self._embedding_model is None:
            raise RuntimeError("RAGClient not initialized — call initialize() first.")
        return Retriever(embedding_model=self._embedding_model)

    # ──────────────────────────────────────────────────────────
    # PROPERTIES
    # ──────────────────────────────────────────────────────────

    @property
    def embedding_model(self) -> EmbeddingModel:
        if self._embedding_model is None:
            raise RuntimeError("RAGClient not initialized.")
        return self._embedding_model

    @property
    def llm_generator(self) -> LLMGenerator:
        if self._llm_generator is None:
            raise RuntimeError("RAGClient not initialized.")
        return self._llm_generator

    def is_initialized(self) -> bool:
        return self._initialized

    def is_paper_indexed(self, paper_id: str) -> bool:
        if paper_id in self._retrievers:
            return self._retrievers[paper_id].size() > 0
        paper_dir = self._faiss_root / paper_id
        return (paper_dir / "index.faiss").exists()

    def get_indexed_papers(self) -> list[str]:
        return list(self._retrievers.keys())

    # ──────────────────────────────────────────────────────────
    # PROCESS PDF
    # ──────────────────────────────────────────────────────────

    async def process_pdf(
        self,
        paper_id: str,
        pdf_path: Path,
    ) -> dict:
        """
        Process a PDF through the full RAG pipeline:
        PDF → Extract → Split → Chunk → Embed → FAISS
        """
        if not self._initialized:
            raise RuntimeError("RAGClient not initialized.")

        if not pdf_path.is_file():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Validate PDF header
        with open(pdf_path, "rb") as f:
            header = f.read(4)
        if header != b"%PDF":
            raise ValueError(f"File is not a valid PDF: {pdf_path}")

        logger.info(f"Processing PDF for paper {paper_id}: {pdf_path}")

        # Run blocking CPU-bound work in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._process_pdf_sync,
            paper_id,
            pdf_path,
        )
        return result

    def _process_pdf_sync(self, paper_id: str, pdf_path: Path) -> dict:
        """Synchronous PDF processing (runs in thread pool)."""
        # 1. Extract pages (returns list[PageContent], each with .blocks)
        extractor = PDFExtractor()
        pages = extractor.extract(pdf_path)

        if not pages:
            raise ValueError("PDF extraction produced no pages.")

        # 2. Split sentences
        splitter = SentenceSplitter()
        sentences = splitter.split(pages)

        if not sentences:
            raise ValueError("No sentences extracted from PDF.")

        # 3. Generate chunks
        chunker = ChunkGenerator(max_characters=2000)
        chunks = chunker.generate(sentences)

        if not chunks:
            raise ValueError("No chunks generated from PDF.")

        # 4. Create retriever and index chunks
        retriever = self._make_retriever()
        retriever.index_chunks(chunks)

        # 5. Save FAISS index to disk
        paper_dir = self._faiss_root / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        retriever.save(paper_dir)

        # 6. Cache retriever in memory
        self._retrievers[paper_id] = retriever

        logger.info(
            f"Paper {paper_id}: {len(pages)} pages, "
            f"{len(sentences)} sentences, "
            f"{len(chunks)} chunks, "
            f"{retriever.size()} vectors indexed."
        )

        return {
            "paper_id": paper_id,
            "pages": len(pages),
            "sentences": len(sentences),
            "chunks": len(chunks),
            "vectors": retriever.size(),
        }

    # ──────────────────────────────────────────────────────────
    # GET RETRIEVER (with lazy load)
    # ──────────────────────────────────────────────────────────

    def _get_retriever(self, paper_id: str) -> Retriever:
        if paper_id in self._retrievers:
            return self._retrievers[paper_id]

        # Try loading from disk
        paper_dir = self._faiss_root / paper_id
        if (paper_dir / "index.faiss").exists():
            retriever = self._make_retriever()
            retriever.load(paper_dir)
            self._retrievers[paper_id] = retriever
            return retriever

        raise KeyError(
            f"Paper '{paper_id}' has not been indexed. "
            "Please analyze the paper first."
        )

    # ──────────────────────────────────────────────────────────
    # ASK (Q&A)
    # ──────────────────────────────────────────────────────────

    async def ask(
        self,
        paper_id: str,
        question: str,
        top_k: int = 8,
    ) -> dict:
        """
        Answer a question about a paper using retrieved context.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._ask_sync,
            paper_id,
            question,
            top_k,
        )

    def _ask_sync(self, paper_id: str, question: str, top_k: int) -> dict:
        retriever = self._get_retriever(paper_id)

        results = retriever.search(question, top_k=top_k)
        if not results:
            return {
                "answer": "No relevant content found in the paper for this question.",
                "sources": [],
            }

        assembler = ContextAssembler(max_context_characters=12000)
        assembled = assembler.assemble(question, results)

        if not assembled.text:
            return {
                "answer": "No usable context could be assembled from the paper.",
                "sources": [],
            }

        generation = self.llm_generator.generate(
            query=question,
            context=assembled.text,
        )

        sources = [
            {
                "chunk_id": item.chunk_id,
                "section": item.section,
                "page_start": item.page_start,
                "page_end": item.page_end,
                "score": round(item.score, 4),
                "text": item.text[:400],
            }
            for item in assembled.items
        ]

        return {
            "answer": generation.answer,
            "model": generation.model,
            "sources": sources,
        }

    # ──────────────────────────────────────────────────────────
    # SUMMARIZE
    # ──────────────────────────────────────────────────────────

    async def summarize(
        self,
        paper_id: str,
        top_k: int = 15,
    ) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._summarize_sync,
            paper_id,
            top_k,
        )

    def _summarize_sync(self, paper_id: str, top_k: int) -> dict:
        retriever = self._get_retriever(paper_id)

        broad_query = (
            "research problem objective methodology experiments results "
            "findings limitations conclusion"
        )
        results = retriever.search(broad_query, top_k=top_k)

        if not results:
            return {"summary": "No content available for summarization."}

        assembler = ContextAssembler(max_context_characters=14000)
        assembled = assembler.assemble(broad_query, results)

        if not assembled.text:
            return {"summary": "Insufficient content for summarization."}

        summarizer = PaperSummarizer(llm_generator=self.llm_generator)
        summary = summarizer.summarize(assembled.text)

        return {"summary": summary}

    # ──────────────────────────────────────────────────────────
    # INFORMATION EXTRACTION
    # ──────────────────────────────────────────────────────────

    async def extract_information(
        self,
        paper_id: str,
        top_k: int = 12,
    ) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._extract_sync,
            paper_id,
            top_k,
        )

    def _extract_sync(self, paper_id: str, top_k: int) -> dict:
        retriever = self._get_retriever(paper_id)

        query = "models datasets metrics results methods experimental settings"
        results = retriever.search(query, top_k=top_k)

        if not results:
            return {
                "models": [], "datasets": [], "metrics": [],
                "results": [], "methods": [], "experimental_settings": [],
            }

        assembler = ContextAssembler(max_context_characters=12000)
        assembled = assembler.assemble(query, results)

        if not assembled.text:
            return {
                "models": [], "datasets": [], "metrics": [],
                "results": [], "methods": [], "experimental_settings": [],
            }

        extractor = InformationExtractor(llm_generator=self.llm_generator)
        return extractor.extract(assembled.text)

    # ──────────────────────────────────────────────────────────
    # RESEARCH GAPS
    # ──────────────────────────────────────────────────────────

    async def research_gaps(
        self,
        paper_id: str,
        top_k: int = 12,
    ) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._gaps_sync,
            paper_id,
            top_k,
        )

    def _gaps_sync(self, paper_id: str, top_k: int) -> dict:
        retriever = self._get_retriever(paper_id)

        query = "limitations future work unresolved questions open problems research gaps"
        results = retriever.search(query, top_k=top_k)

        if not results:
            return {
                "limitations": [], "unresolved_questions": [],
                "future_work": [], "research_gaps": [],
            }

        assembler = ContextAssembler(max_context_characters=12000)
        assembled = assembler.assemble(query, results)

        if not assembled.text:
            return {
                "limitations": [], "unresolved_questions": [],
                "future_work": [], "research_gaps": [],
            }

        detector = ResearchGapDetector(llm_generator=self.llm_generator)
        return detector.detect(assembled.text)

    # ──────────────────────────────────────────────────────────
    # CITATION VERIFICATION
    # ──────────────────────────────────────────────────────────

    async def verify_citations(
        self,
        paper_id: str,
        answer: str,
        top_k: int = 8,
    ) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._verify_sync,
            paper_id,
            answer,
            top_k,
        )

    def _verify_sync(self, paper_id: str, answer: str, top_k: int) -> dict:
        retriever = self._get_retriever(paper_id)

        results = retriever.search(answer, top_k=top_k)

        if not results:
            return {"verified": False, "claims": []}

        assembler = ContextAssembler(max_context_characters=12000)
        assembled = assembler.assemble(answer, results)

        if not assembled.text:
            return {"verified": False, "claims": []}

        verifier = CitationVerifier(llm_generator=self.llm_generator)
        return verifier.verify(answer=answer, context=assembled.text)

    # ──────────────────────────────────────────────────────────
    # PAPER COMPARISON
    # ──────────────────────────────────────────────────────────

    async def compare_papers(
        self,
        paper_id_a: str,
        paper_id_b: str,
        top_k: int = 10,
    ) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._compare_sync,
            paper_id_a,
            paper_id_b,
            top_k,
        )

    def _compare_sync(
        self,
        paper_id_a: str,
        paper_id_b: str,
        top_k: int,
    ) -> dict:
        retriever_a = self._get_retriever(paper_id_a)
        retriever_b = self._get_retriever(paper_id_b)

        comparison_query = (
            "objective methodology models datasets metrics results "
            "experimental settings limitations research gaps"
        )

        results_a = retriever_a.search(comparison_query, top_k=top_k)
        results_b = retriever_b.search(comparison_query, top_k=top_k)

        assembler = ContextAssembler(max_context_characters=8000)
        context_a = assembler.assemble(comparison_query, results_a).text
        context_b = assembler.assemble(comparison_query, results_b).text

        if not context_a:
            raise KeyError(f"No context available for paper A ({paper_id_a}).")
        if not context_b:
            raise KeyError(f"No context available for paper B ({paper_id_b}).")

        comparator = PaperComparator(llm_generator=self.llm_generator)
        return comparator.compare(
            paper_a_context=context_a,
            paper_b_context=context_b,
        )


# ──────────────────────────────────────────────────────────────────────────────
# SINGLETON ACCESSOR
# ──────────────────────────────────────────────────────────────────────────────

def get_rag_client() -> RAGClient:
    """Return the global RAGClient singleton."""
    return RAGClient.get_instance()

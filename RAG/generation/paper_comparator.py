from __future__ import annotations

from RAG.generation.llm_generator import (
    LLMGenerator,
)


class PaperComparator:
    """
    Compares two research papers using only the supplied
    evidence from each paper.

    The comparator does not perform retrieval itself.

    The LLM returns a concise Markdown comparison instead
    of forced JSON. This is more reliable with local LLMs
    such as Llama 3.2 running through Ollama.
    """

    def __init__(
        self,
        llm_generator: LLMGenerator,
    ) -> None:

        self.llm_generator = (
            llm_generator
        )

    def compare(
        self,
        paper_a_context: str,
        paper_b_context: str,
    ) -> dict:
        """
        Compare two papers using their supplied contexts.
        """

        paper_a_context = (
            paper_a_context.strip()
        )

        paper_b_context = (
            paper_b_context.strip()
        )

        if not paper_a_context:
            raise ValueError(
                "Paper A context cannot be empty."
            )

        if not paper_b_context:
            raise ValueError(
                "Paper B context cannot be empty."
            )

        prompt = self._build_prompt(
            paper_a_context=paper_a_context,
            paper_b_context=paper_b_context,
        )

        result = (
            self.llm_generator.generate(
                query=(
                    "Compare Paper A and Paper B "
                    "using only the supplied evidence."
                ),
                context=prompt,
            )
        )

        answer = result.answer.strip()

        if not answer:
            raise ValueError(
                "LLM returned an empty comparison."
            )

        return {
            "comparison": answer,
        }

    def _build_prompt(
        self,
        paper_a_context: str,
        paper_b_context: str,
    ) -> str:
        """
        Build a concise comparison prompt.

        Markdown is intentionally used instead of JSON
        because local LLMs are substantially more reliable
        at producing concise textual structure.
        """

        return f"""
You are ResearchPilot, an AI research paper
comparison assistant.

Compare PAPER A and PAPER B using ONLY the
information supplied below.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent facts.
3. Do not invent numerical results.
4. Preserve numerical values exactly.
5. If information is unavailable, write:
   "Not specified in the provided context."
6. Do not assume missing information means that
   the paper does not contain it.
7. Do not automatically say one paper is better.
8. Only compare results when the supplied evidence
   allows a meaningful comparison.
9. Keep the answer concise.
10. Use ONLY the supplied evidence.

Return the comparison using EXACTLY these headings:

## Objective

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Methodology

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Models

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Datasets

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Metrics

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Results

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Experimental Settings

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Limitations

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Research Gaps

**Paper A:** ...
**Paper B:** ...
**Comparison:** ...

## Overall Comparison

...

Do not add any other sections.

PAPER A:

{paper_a_context}

PAPER B:

{paper_b_context}

Now produce the comparison.
""".strip()
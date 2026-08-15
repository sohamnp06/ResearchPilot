from __future__ import annotations

from RAG.generation.llm_generator import (
    LLMGenerator,
)


class PaperSummarizer:
    """
    Generates structured research-paper summaries
    from supplied research context.

    The summarizer does not retrieve documents itself.
    It operates on context supplied by the retrieval
    pipeline.
    """

    def __init__(
        self,
        llm_generator: LLMGenerator,
    ) -> None:

        self.llm_generator = (
            llm_generator
        )

    def summarize(
        self,
        context: str,
    ) -> str:
        """
        Generate a structured summary from research
        context.
        """

        context = context.strip()

        if not context:
            raise ValueError(
                "Context cannot be empty."
            )

        prompt = self._build_prompt(
            context
        )

        result = (
            self.llm_generator.generate(
                query=(
                    "Summarize the research paper "
                    "using the provided context."
                ),
                context=prompt,
            )
        )

        return result.answer

    def _build_prompt(
        self,
        context: str,
    ) -> str:
        """
        Build the research-paper summarization prompt.
        """

        return f"""
You are ResearchPilot, an AI research assistant.

Create a structured summary of the research content
provided below.

Use ONLY the information contained in the context.

Do not invent facts, results, methods, datasets,
limitations, or conclusions.

Organize the summary using these sections when the
information is available:

1. Research Problem
2. Objective
3. Methodology
4. Experiments / Dataset
5. Key Results
6. Main Findings
7. Limitations
8. Conclusion

If a section is not supported by the provided context,
write:

"Not specified in the provided context."

Keep numerical results exactly as stated.

RESEARCH CONTEXT:
{context}

STRUCTURED SUMMARY:
""".strip()
from __future__ import annotations

import json
import re

from RAG.generation.llm_generator import (
    LLMGenerator,
)


class ResearchGapDetector:
    """
    Detects research gaps, limitations, unresolved questions,
    and future-work directions from supplied research context.

    The detector does not perform retrieval and does not use
    outside knowledge. It only analyzes the supplied context.
    """

    def __init__(
        self,
        llm_generator: LLMGenerator,
    ) -> None:

        self.llm_generator = (
            llm_generator
        )

    def detect(
        self,
        context: str,
    ) -> dict:
        """
        Detect research gaps supported by the context.
        """

        context = context.strip()

        if not context:
            raise ValueError(
                "Context cannot be empty."
            )

        prompt = self._build_prompt(
            context
        )

        result = self.llm_generator.generate(
            query=(
                "Identify research gaps, limitations, "
                "unresolved questions, and future work "
                "from the research context."
            ),
            context=prompt,
        )

        return self._parse_response(
            result.answer
        )

    def _build_prompt(
        self,
        context: str,
    ) -> str:
        """
        Build a grounded research-gap detection prompt.
        """

        return f"""
You are ResearchPilot, a research analysis assistant.

Analyze the research context below and identify research
gaps that are explicitly supported by the provided text.

Use ONLY the provided context.

Do NOT use outside knowledge.
Do NOT invent limitations or weaknesses.
Do NOT assume that something is a research gap simply
because it was not mentioned in the context.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "limitations": [],
  "unresolved_questions": [],
  "future_work": [],
  "research_gaps": []
}}

Definitions:

- limitations:
  Limitations or constraints explicitly stated by the
  authors.

- unresolved_questions:
  Questions or issues that the authors explicitly indicate
  are not yet understood or resolved.

- future_work:
  Future research directions explicitly suggested by
  the authors.

- research_gaps:
  Research gaps that can be directly derived from the
  limitations, unresolved questions, or future-work
  statements in the supplied context.

Rules:

1. Every item must be supported by the supplied context.
2. Do not create generic research gaps.
3. Do not introduce information from outside the paper.
4. Keep technical terminology accurate.
5. If a category is not supported, return an empty list.
6. Keep the output concise.
7. Return valid JSON only.

RESEARCH CONTEXT:

{context}

JSON:
""".strip()

    def _parse_response(
        self,
        response: str,
    ) -> dict:
        """
        Parse and validate the LLM JSON response.
        """

        response = response.strip()

        response = re.sub(
            r"^```(?:json)?\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        try:
            data = json.loads(
                response
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        required_fields = {
            "limitations",
            "unresolved_questions",
            "future_work",
            "research_gaps",
        }

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        missing = (
            required_fields
            - set(data.keys())
        )

        if missing:
            raise ValueError(
                "Missing research-gap fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        for field in required_fields:

            if not isinstance(
                data[field],
                list,
            ):
                raise ValueError(
                    f"Field '{field}' must be a list."
                )

        return data
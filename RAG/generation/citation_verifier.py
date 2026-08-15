from __future__ import annotations

import json
import re

from RAG.generation.llm_generator import (
    LLMGenerator,
)


class CitationVerifier:
    """
    Verifies whether generated claims are supported by
    the supplied research sources.

    The verifier does not retrieve documents itself.
    It checks generated claims against the provided
    source context.
    """

    def __init__(
        self,
        llm_generator: LLMGenerator,
    ) -> None:

        self.llm_generator = (
            llm_generator
        )

    def verify(
        self,
        answer: str,
        context: str,
    ) -> dict:
        """
        Verify whether claims in an answer are supported
        by the supplied research context.
        """

        answer = answer.strip()
        context = context.strip()

        if not answer:
            raise ValueError(
                "Answer cannot be empty."
            )

        if not context:
            raise ValueError(
                "Context cannot be empty."
            )

        prompt = self._build_prompt(
            answer=answer,
            context=context,
        )

        result = self.llm_generator.generate(
            query=(
                "Verify whether the answer claims "
                "are supported by the research sources."
            ),
            context=prompt,
        )

        return self._parse_response(
            result.answer
        )

    def _build_prompt(
        self,
        answer: str,
        context: str,
    ) -> str:
        """
        Build the citation verification prompt.
        """

        return f"""
You are ResearchPilot, a research citation verifier.

Your task is to verify whether the claims made in the
ANSWER are supported by the RESEARCH SOURCES.

Use ONLY the supplied research sources.

Do not use outside knowledge.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "verified": true,
  "claims": [
    {{
      "claim": "...",
      "supported": true,
      "sources": ["chunk_00000"],
      "reason": "..."
    }}
  ]
}}

Rules:

1. Break the answer into meaningful factual claims.
2. Check each claim against the supplied sources.
3. A claim is supported only if the source contains
   sufficient information to support it.
4. Do not treat semantic similarity alone as proof.
5. Preserve source chunk IDs exactly.
6. If a claim is unsupported, set "supported" to false.
7. The overall "verified" value should be true only if
   all meaningful factual claims are supported.
8. Do not invent source IDs.
9. Return JSON only.

ANSWER:

{answer}

RESEARCH SOURCES:

{context}

JSON:
""".strip()

    def _parse_response(
        self,
        response: str,
    ) -> dict:
        """
        Parse and validate the verification response.
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

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Verification response must be a JSON object."
            )

        if "verified" not in data:
            raise ValueError(
                "Missing 'verified' field."
            )

        if "claims" not in data:
            raise ValueError(
                "Missing 'claims' field."
            )

        if not isinstance(
            data["verified"],
            bool,
        ):
            raise ValueError(
                "'verified' must be a boolean."
            )

        if not isinstance(
            data["claims"],
            list,
        ):
            raise ValueError(
                "'claims' must be a list."
            )

        for claim in data["claims"]:

            if not isinstance(
                claim,
                dict,
            ):
                raise ValueError(
                    "Each claim must be an object."
                )

            required_fields = {
                "claim",
                "supported",
                "sources",
                "reason",
            }

            missing = (
                required_fields
                - set(claim.keys())
            )

            if missing:
                raise ValueError(
                    "Missing claim fields: "
                    + ", ".join(
                        sorted(missing)
                    )
                )

            if not isinstance(
                claim["supported"],
                bool,
            ):
                raise ValueError(
                    "'supported' must be boolean."
                )

            if not isinstance(
                claim["sources"],
                list,
            ):
                raise ValueError(
                    "'sources' must be a list."
                )

        return data
from __future__ import annotations

import json
import re

from RAG.generation.llm_generator import (
    LLMGenerator,
)


class InformationExtractor:
    """
    Extracts structured research information from
    retrieved document context.

    The extractor does not perform retrieval.
    It only extracts information supported by the
    supplied context.
    """

    def __init__(
        self,
        llm_generator: LLMGenerator,
    ) -> None:

        self.llm_generator = llm_generator

    def extract(
        self,
        context: str,
    ) -> dict:
        """
        Extract structured research information.
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
                "Extract structured research "
                "information from the context."
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
        Build a structured extraction prompt.
        """

        return f"""
You are ResearchPilot, an AI research information
extraction system.

Extract research information ONLY from the provided
context.

Do not use outside knowledge.
Do not invent missing information.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "models": [],
  "datasets": [],
  "metrics": [],
  "results": [],
  "methods": [],
  "experimental_settings": []
}}

Rules:

- models: model or architecture names explicitly
  mentioned in the context.
- datasets: datasets explicitly mentioned.
- metrics: evaluation metrics explicitly mentioned.
- results: important numerical or qualitative results.
- methods: important methods or techniques described.
- experimental_settings: important training or
  evaluation settings explicitly stated.

Keep numerical values exactly as they appear.

If a category has no supported information,
return an empty list.

Do not add explanations outside the JSON.

RESEARCH CONTEXT:

{context}

JSON:
""".strip()

    def _parse_response(
        self,
        response: str,
    ) -> dict:
        """
        Parse the LLM JSON response safely.
        """

        response = response.strip()

        # Remove markdown code fences if the model
        # happens to return them.
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
            data = json.loads(response)
        except json.JSONDecodeError:
            # Smaller local models sometimes add one explanatory sentence
            # before or after an otherwise valid JSON object.
            match = re.search(r"\{.*\}", response, flags=re.DOTALL)
            if not match:
                raise ValueError("LLM returned invalid JSON.") from None
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise ValueError("LLM returned invalid JSON.") from exc

        required_fields = {
            "models",
            "datasets",
            "metrics",
            "results",
            "methods",
            "experimental_settings",
        }

        if not isinstance(data, dict):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        missing = (
            required_fields
            - set(data.keys())
        )

        if missing:
            raise ValueError(
                "Missing extraction fields: "
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

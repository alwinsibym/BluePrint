import json
import logging
import re
from app.services.base_service import BaseService
import app.llm.ollama_client as ollama_client
from app.models.requirements import RequirementsResponse
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RequirementsService(BaseService):
    """Orchestrates prompt loading, LLM invocation, JSON parsing and validation
    for the Requirements Agent.

    Retry behaviour is controlled by ``settings.REQUIREMENTS_AGENT_RETRY_COUNT``.
    """

    def description(self) -> str:
        return "Generates a structured requirements document from a project idea."

    async def generate_requirements(self, idea: str) -> RequirementsResponse:
        """Generate and validate a RequirementsResponse for the given idea.

        Tries up to ``REQUIREMENTS_AGENT_RETRY_COUNT`` times to obtain valid JSON
        from the LLM before raising an HTTP 422 error.
        """
        template = self.load_prompt("requirements")
        prompt = template.replace("{{idea}}", idea)

        max_attempts = max(1, settings.REQUIREMENTS_AGENT_RETRY_COUNT)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            logger.info("RequirementsService: LLM attempt %d/%d", attempt, max_attempts)
            try:
                raw = await ollama_client.generate(prompt)
                parsed = self._extract_json(raw)
                return RequirementsResponse(**parsed)
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                logger.warning("Attempt %d failed to parse LLM response: %s", attempt, exc)
                last_error = exc

        raise HTTPException(
            status_code=422,
            detail=f"LLM returned malformed JSON after {max_attempts} attempt(s). "
                   f"Last error: {last_error}",
        )

    @staticmethod
    def _extract_json(raw: str) -> dict:
        """Strip markdown fences and extract the first valid JSON object."""
        # Remove markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", raw).strip()
        # Find the first { … } block
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in LLM response.")
        json_str = cleaned[start:end]
        return json.loads(json_str)


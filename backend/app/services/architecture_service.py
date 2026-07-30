import json
import logging
import re
from app.services.base_service import BaseService
import app.llm.ollama_client as ollama_client
from app.models.architecture import ArchitectureResponse
from app.models.requirements import RequirementsResponse
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ArchitectureService(BaseService):
    """Orchestrates prompt loading, LLM invocation, JSON parsing and validation
    for the Architecture Agent.
    """

    def description(self) -> str:
        return "Generates a structured software architecture from project requirements."

    async def generate_architecture(self, requirements: RequirementsResponse) -> ArchitectureResponse:
        """Generate and validate an ArchitectureResponse for the given requirements.
        """
        template = self.load_prompt("architecture")
        
        # We pass the requirements as a formatted JSON string to the prompt
        req_json = requirements.model_dump_json(indent=2)
        prompt = template.replace("{{requirements}}", req_json)

        max_attempts = max(1, settings.REQUIREMENTS_AGENT_RETRY_COUNT)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            logger.info("ArchitectureService: LLM attempt %d/%d", attempt, max_attempts)
            try:
                raw = await ollama_client.generate(prompt)
                parsed = self._extract_json(raw)
                return ArchitectureResponse(**parsed)
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
        cleaned = re.sub(r"```(?:json)?", "", raw).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in LLM response.")
        json_str = cleaned[start:end]
        return json.loads(json_str)

import json
import logging
import re
from app.services.base_service import BaseService
import app.llm.ollama_client as ollama_client
from app.models.database import DatabaseResponse
from app.models.requirements import ProjectContext
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DatabaseService(BaseService):
    """Orchestrates prompt loading, LLM invocation, JSON parsing and validation
    for the Database Agent.
    """

    def description(self) -> str:
        return "Generates database entities, SQLite-optimized SQL schema, and Mermaid ER diagram based on ProjectContext."

    async def generate_database(self, context: ProjectContext) -> DatabaseResponse:
        """Generate and validate a DatabaseResponse for the given ProjectContext."""
        template = self.load_prompt("database")
        
        # Pass formatted JSON string of ProjectContext to prompt
        context_json = context.model_dump_json(indent=2)
        prompt = template.replace("{{project_context}}", context_json)

        max_attempts = max(1, settings.REQUIREMENTS_AGENT_RETRY_COUNT)
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            logger.info("DatabaseService: LLM attempt %d/%d", attempt, max_attempts)
            try:
                raw = await ollama_client.generate(prompt)
                parsed = self._extract_json(raw)
                return DatabaseResponse(**parsed)
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

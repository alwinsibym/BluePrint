from app.agents.base_agent import BaseAgent
from app.services.requirements_service import RequirementsService
from app.models.requirements import RequirementsResponse

class RequirementsAgent(BaseAgent):
    """Agent that converts a project idea into a structured requirements document.

    Delegates all LLM interaction and JSON validation to ``RequirementsService``,
    keeping the agent layer thin and suitable for future CrewAI orchestration.
    """

    def __init__(self, service: RequirementsService) -> None:
        self._service = service

    async def handle(self, idea: str) -> RequirementsResponse:  # type: ignore[override]
        """Forward the idea to the service and return a validated response."""
        return await self._service.generate_requirements(idea)

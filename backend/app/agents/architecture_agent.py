from app.agents.base_agent import BaseAgent
from app.services.architecture_service import ArchitectureService
from app.models.requirements import RequirementsResponse
from app.models.architecture import ArchitectureResponse

class ArchitectureAgent(BaseAgent):
    """Agent that designs a high-level architecture based on project requirements.

    Delegates all LLM interaction and JSON validation to ``ArchitectureService``.
    """

    def __init__(self, service: ArchitectureService) -> None:
        self._service = service

    async def handle(self, requirements: RequirementsResponse) -> ArchitectureResponse:  # type: ignore[override]
        """Forward the requirements to the service and return a validated response."""
        return await self._service.generate_architecture(requirements)

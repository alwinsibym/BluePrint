from app.agents.base_agent import BaseAgent
from app.services.documentation_service import DocumentationService
from app.models.requirements import ProjectContext
from app.models.documentation import DocumentationResponse

class DocumentationAgent(BaseAgent):
    """Agent that generates project documentation based on complete ProjectContext.

    Delegates all LLM interaction and JSON validation to ``DocumentationService``.
    """

    def __init__(self, service: DocumentationService) -> None:
        self._service = service

    async def handle(self, context: ProjectContext) -> DocumentationResponse:  # type: ignore[override]
        """Forward the ProjectContext to the service and return a validated response."""
        return await self._service.generate_documentation(context)

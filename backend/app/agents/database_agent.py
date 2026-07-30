from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.models.requirements import ProjectContext
from app.models.database import DatabaseResponse

class DatabaseAgent(BaseAgent):
    """Agent that designs the database schema based on complete ProjectContext.

    Delegates all LLM interaction and JSON validation to ``DatabaseService``.
    """

    def __init__(self, service: DatabaseService) -> None:
        self._service = service

    async def handle(self, context: ProjectContext) -> DatabaseResponse:  # type: ignore[override]
        """Forward the ProjectContext to the service and return a validated response."""
        return await self._service.generate_database(context)

"""
Scaffold Service
----------------
Thin wrapper around ``ScaffoldAgent`` that provides the service interface
expected by the scaffold API endpoint.
"""

from __future__ import annotations

from app.agents.scaffold_agent import ScaffoldAgent
from app.models.requirements import ProjectContext
from app.models.scaffold import ScaffoldResponse
from app.services.base_service import BaseService


class ScaffoldService(BaseService):
    """Delegates project generation to ``ScaffoldAgent``."""

    def __init__(self) -> None:
        self._agent = ScaffoldAgent()

    def description(self) -> str:
        return (
            "Assembles a complete, development‑ready project skeleton from the "
            "accumulated ProjectContext using the Project Generator pipeline."
        )

    async def generate_scaffold(self, context: ProjectContext) -> ScaffoldResponse:
        """Run the Scaffold Agent and return the generated project data."""
        return await self._agent.handle(context)

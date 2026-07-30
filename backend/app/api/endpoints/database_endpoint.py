from fastapi import APIRouter, Depends
from app.models.requirements import ProjectContext
from app.models.database import DatabaseResponse
from app.services.database_service import DatabaseService
from app.agents.database_agent import DatabaseAgent

router = APIRouter()

def get_database_agent() -> DatabaseAgent:
    return DatabaseAgent(DatabaseService())

@router.post(
    "/agents/database",
    response_model=DatabaseResponse,
    summary="Generate database schema and ER diagram from ProjectContext",
    description="Takes a complete ProjectContext (Requirements + Architecture) and generates entities, SQLite SQL schema, and Mermaid ER diagram.",
    tags=["agents"],
)
async def create_database(
    context: ProjectContext,
    agent: DatabaseAgent = Depends(get_database_agent),
) -> DatabaseResponse:
    return await agent.handle(context)

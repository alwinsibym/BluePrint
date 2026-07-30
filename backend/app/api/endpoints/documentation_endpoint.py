from fastapi import APIRouter, Depends
from app.models.requirements import ProjectContext
from app.models.documentation import DocumentationResponse
from app.services.documentation_service import DocumentationService
from app.agents.documentation_agent import DocumentationAgent

router = APIRouter()

def get_documentation_agent() -> DocumentationAgent:
    return DocumentationAgent(DocumentationService())

@router.post(
    "/agents/documentation",
    response_model=DocumentationResponse,
    summary="Generate documentation from ProjectContext",
    description="Takes a complete ProjectContext (Requirements + Architecture + Database) and generates README.md, setup guides, API specs, and developer notes.",
    tags=["agents"],
)
async def create_documentation(
    context: ProjectContext,
    agent: DocumentationAgent = Depends(get_documentation_agent),
) -> DocumentationResponse:
    return await agent.handle(context)

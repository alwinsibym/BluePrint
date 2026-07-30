from fastapi import APIRouter, Depends
from app.models.requirements import RequirementsResponse
from app.models.architecture import ArchitectureResponse
from app.services.architecture_service import ArchitectureService
from app.agents.architecture_agent import ArchitectureAgent

router = APIRouter()

def get_architecture_agent() -> ArchitectureAgent:
    return ArchitectureAgent(ArchitectureService())

@router.post(
    "/agents/architecture",
    response_model=ArchitectureResponse,
    summary="Generate software architecture from requirements",
    description="Takes a structured Requirements document and generates a high-level architecture design, component breakdown, and folder structure.",
    tags=["agents"],
)
async def create_architecture(
    requirements: RequirementsResponse,
    agent: ArchitectureAgent = Depends(get_architecture_agent),
) -> ArchitectureResponse:
    return await agent.handle(requirements)

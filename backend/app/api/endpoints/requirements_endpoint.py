from fastapi import APIRouter, Depends
from app.models.requirements import RequirementsRequest, RequirementsResponse
from app.services.requirements_service import RequirementsService
from app.agents.requirements_agent import RequirementsAgent

router = APIRouter()


def get_requirements_agent() -> RequirementsAgent:
    """Dependency factory — keeps the API layer decoupled from agent internals.

    Future CrewAI integration can replace this factory without touching the
    route handler.
    """
    return RequirementsAgent(RequirementsService())


@router.post(
    "/agents/requirements",
    response_model=RequirementsResponse,
    summary="Generate a structured requirements document",
    description=(
        "Accepts a natural‑language software project idea and returns a "
        "primary planning document with objectives, functional requirements, "
        "user stories, tech‑stack recommendations, and more."
    ),
    tags=["agents"],
)
async def create_requirements(
    req: RequirementsRequest,
    agent: RequirementsAgent = Depends(get_requirements_agent),
) -> RequirementsResponse:
    return await agent.handle(req.idea)

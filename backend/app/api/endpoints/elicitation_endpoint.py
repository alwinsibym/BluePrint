"""
elicitation_endpoint.py
───────────────────────
Exposes two endpoints for the interactive requirements elicitation engine:

  POST /elicit/start   — Start a new interview session, returns first question.
  POST /elicit/chat    — Send an answer, receive next question or final requirements.

Both endpoints are stateless. The frontend is responsible for maintaining
the conversation history and passing it with every request.
"""
from fastapi import APIRouter
from app.models.elicitation import (
    ElicitationStartRequest,
    ElicitationStartResponse,
    ElicitationChatRequest,
    ElicitationChatResponse,
)
from app.services.elicitation_service import ElicitationService

router = APIRouter()
_service = ElicitationService()


@router.post(
    "/elicit/start",
    response_model=ElicitationChatResponse,
    summary="Start an interactive requirements elicitation interview",
    description=(
        "Accepts the initial project idea and returns the first elicitation question. "
        "The system follows BABOK v3 methodology across 6 structured phases. "
        "The response includes the conversation history that must be sent back with every /elicit/chat call."
    ),
    tags=["elicitation"],
)
async def elicit_start(req: ElicitationStartRequest) -> ElicitationChatResponse:
    return await _service.start(req.idea)


@router.post(
    "/elicit/chat",
    response_model=ElicitationChatResponse,
    summary="Send an answer and receive the next elicitation question",
    description=(
        "Accepts the developer's answer along with the full conversation history. "
        "Returns the next question, or — when all phases are complete — the final "
        "synthesised RequirementsResponse extracted from the interview transcript."
    ),
    tags=["elicitation"],
)
async def elicit_chat(req: ElicitationChatRequest) -> ElicitationChatResponse:
    return await _service.chat(req.idea, req.user_answer, req.history)

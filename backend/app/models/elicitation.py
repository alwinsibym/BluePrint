"""
elicitation.py
──────────────
Pydantic models for the Interactive Requirements Elicitation Engine.
The session is fully stateless — the frontend passes the full conversation
history with every request so no server-side session storage is needed.
"""
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.models.requirements import RequirementsResponse


class ElicitationMessage(BaseModel):
    """A single turn in the elicitation conversation."""
    role: Literal["assistant", "user"]
    content: str
    phase: int = Field(default=1, description="Which elicitation phase this message belongs to")


class ElicitationStartRequest(BaseModel):
    """Frontend sends this to kick off an interview."""
    idea: str = Field(..., description="The initial project idea described by the developer")


class ElicitationStartResponse(BaseModel):
    """Backend returns the first question and an empty history."""
    question: str
    phase: int
    phase_label: str
    phase_description: str
    progress_pct: int
    history: List[ElicitationMessage]
    is_complete: bool = False
    requirements: Optional[RequirementsResponse] = None


class ElicitationChatRequest(BaseModel):
    """Frontend sends user answer + full history on every turn."""
    idea: str
    user_answer: str
    history: List[ElicitationMessage]


class ElicitationChatResponse(BaseModel):
    """Backend returns the next question, or final requirements when complete."""
    question: str
    phase: int
    phase_label: str
    phase_description: str
    progress_pct: int
    history: List[ElicitationMessage]
    is_complete: bool = False
    requirements: Optional[RequirementsResponse] = None

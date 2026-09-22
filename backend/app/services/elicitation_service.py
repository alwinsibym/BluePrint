"""
elicitation_service.py
──────────────────────
The core intelligence behind the Interactive Requirements Elicitation Engine.

Methodology: BABOK v3 / IEEE 29148-2018 structured elicitation interview.

The AI acts as a Requirements Engineer (BA) and guides the developer through
6 structured phases. Each phase focuses on a distinct RE concern. After the
final phase, the service synthesises all Q&A pairs into a formal
RequirementsResponse JSON — grounded in the developer's own domain knowledge,
not AI hallucination.

Key design decisions:
  - Fully STATELESS: the entire conversation history is passed with every call.
  - The LLM is asked to return a single, focused question per turn (not a list).
  - Synthesis uses a structured prompt + JSON extraction identical to the
    existing RequirementsService, so the output is fully compatible.
"""
from __future__ import annotations

import json
import logging
import re
from typing import List, Tuple

import app.llm.ollama_client as ollama_client
from app.models.elicitation import ElicitationMessage, ElicitationChatResponse
from app.models.requirements import RequirementsResponse
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# ── Phase definitions ──────────────────────────────────────────────────────────
# Each phase has: (label, description, questions_count, system_context)
PHASES: List[Tuple[str, str, int, str]] = [
    (
        "Stakeholders & Context",
        "Identifying who the system is for and the problem it solves",
        2,
        "You are gathering context: who are the stakeholders, who will use this system, "
        "and what pain points or problems currently exist that this system will address.",
    ),
    (
        "Goals & Success Criteria",
        "Defining what success looks like and core objectives",
        2,
        "You are identifying the project's goals: what the system MUST accomplish, "
        "how they will know the project is a success, and what failure would look like.",
    ),
    (
        "Core Features & User Workflows",
        "Mapping primary use cases and key user journeys",
        3,
        "You are eliciting core functionality: what the primary users do in the system "
        "step-by-step, which features are essential vs. nice-to-have, and the most "
        "important user workflows.",
    ),
    (
        "System Boundaries & Integrations",
        "Defining scope, external systems, and what is out of scope",
        2,
        "You are defining boundaries: what external systems or APIs must this integrate with, "
        "what is explicitly OUT of scope for version 1, and what data comes in/out of the system.",
    ),
    (
        "Quality & Constraints",
        "Non-functional requirements, performance, security, and tech preferences",
        2,
        "You are gathering quality requirements: expected user load, performance expectations, "
        "security or compliance needs, budget or technology constraints, and any platform "
        "preferences the developer already has.",
    ),
    (
        "Edge Cases & Risks",
        "Identifying risks, failure modes, and tricky scenarios",
        2,
        "You are gathering completeness information: what could go wrong, tricky edge cases "
        "or special scenarios the system must handle, and any known risks or assumptions "
        "the developer is aware of.",
    ),
]

TOTAL_QUESTIONS = sum(p[2] for p in PHASES)


def _compute_phase_and_q_index(history: List[ElicitationMessage]) -> Tuple[int, int, int]:
    """
    From the conversation history, determine:
      - current 0-indexed phase
      - 0-indexed question number within that phase
      - overall question number (0-indexed) for progress calculation
    """
    # Count assistant turns (each = one question asked)
    asked = sum(1 for m in history if m.role == "assistant")
    overall_q = asked  # 0-indexed next question to ask

    cumulative = 0
    for phase_idx, (_, _, q_count, _) in enumerate(PHASES):
        if overall_q < cumulative + q_count:
            return phase_idx, overall_q - cumulative, overall_q
        cumulative += q_count

    # All phases complete
    return len(PHASES), 0, overall_q


def _build_question_prompt(
    idea: str,
    phase_idx: int,
    q_in_phase: int,
    history: List[ElicitationMessage],
) -> str:
    phase_label, _, _, phase_context = PHASES[phase_idx]

    history_text = ""
    for msg in history:
        speaker = "Business Analyst" if msg.role == "assistant" else "Developer"
        history_text += f"{speaker}: {msg.content}\n"

    prompt = f"""You are an expert Requirements Engineer / Business Analyst conducting a structured 
requirements elicitation interview using BABOK v3 methodology.

PROJECT IDEA:
{idea}

CURRENT PHASE: Phase {phase_idx + 1} of {len(PHASES)} — "{phase_label}"
PHASE CONTEXT: {phase_context}

CONVERSATION SO FAR:
{history_text if history_text else "(This is the first question — no conversation yet.)"}

INSTRUCTIONS:
- Ask exactly ONE focused, open-ended question relevant to "{phase_label}" (Phase {phase_idx + 1}).
- This is question {q_in_phase + 1} within this phase.
- Your question must help uncover real, specific requirements — not generic questions.
- Be concise (1–3 sentences maximum). Do not give preamble or say "sure" or "great".
- Do not number the question or add bullet points.
- Directly ask the question, written as a professional BA would in a real meeting.
- Do NOT synthesise requirements yet — only ask the question.

Your question:"""

    return prompt


def _build_synthesis_prompt(idea: str, history: List[ElicitationMessage]) -> str:
    qa_pairs = []
    messages = list(history)
    i = 0
    while i < len(messages):
        if messages[i].role == "assistant":
            question = messages[i].content
            answer = messages[i + 1].content if (i + 1 < len(messages) and messages[i + 1].role == "user") else "(no answer)"
            phase_idx = min(messages[i].phase - 1, len(PHASES) - 1)
            phase_label = PHASES[phase_idx][0]
            qa_pairs.append(f"[{phase_label}] Q: {question}\n  A: {answer}")
            i += 2
        else:
            i += 1

    qa_text = "\n\n".join(qa_pairs)

    prompt = f"""You are an expert Requirements Engineer. Based on a structured elicitation interview 
conducted following BABOK v3 methodology, synthesise the developer's answers into a formal 
Software Requirements Specification (SRS) aligned to IEEE Std 830-1998.

ORIGINAL PROJECT IDEA:
{idea}

ELICITATION INTERVIEW TRANSCRIPT:
{qa_text}

INSTRUCTIONS:
- Extract requirements ONLY from what the developer explicitly stated in their answers.
- Do NOT invent or hallucinate requirements not mentioned by the developer.
- If the developer did not mention something, omit it or mark it as TBD.
- Use professional SRS language (e.g., "The system SHALL...", "Users SHALL be able to...").
- Infer a sensible project name and overview from the idea and answers.
- recommended_tech_stack should reflect any preferences the developer mentioned, otherwise suggest sensible defaults.

Return ONLY valid JSON matching this exact schema (no markdown fences, no commentary):
{{
  "project_name": "string",
  "project_overview": "string (2–4 sentences summarising what was learned)",
  "objectives": ["string", ...],
  "functional_requirements": ["string (each starts with 'The system shall...')", ...],
  "non_functional_requirements": ["string (performance, security, scalability, etc.)", ...],
  "user_roles": ["string", ...],
  "user_stories": [
    {{"role": "string", "desire": "string", "benefit": "string"}},
    ...
  ],
  "suggested_modules": ["string", ...],
  "assumptions": ["string", ...],
  "constraints": ["string", ...],
  "recommended_tech_stack": {{
    "frontend": "string",
    "backend": "string",
    "database": "string",
    "ai_framework": "string"
  }},
  "future_scope": ["string", ...]
}}"""

    return prompt


def _extract_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(cleaned[start:end])


class ElicitationService:
    """
    Manages the guided requirements elicitation interview.

    Phase lifecycle:
      start()  → returns first question (Phase 1, Q1)
      chat()   → returns next question or (when complete) final RequirementsResponse
    """

    async def start(self, idea: str) -> ElicitationChatResponse:
        """Generate the very first elicitation question."""
        prompt = _build_question_prompt(idea, phase_idx=0, q_in_phase=0, history=[])
        question = await self._ask_llm(prompt)

        first_msg = ElicitationMessage(role="assistant", content=question, phase=1)
        phase_label, phase_desc, _, _ = PHASES[0]

        return ElicitationChatResponse(
            question=question,
            phase=1,
            phase_label=phase_label,
            phase_description=phase_desc,
            progress_pct=0,
            history=[first_msg],
            is_complete=False,
        )

    async def chat(
        self, idea: str, user_answer: str, history: List[ElicitationMessage]
    ) -> ElicitationChatResponse:
        """
        Process the developer's answer and either:
          - return the next question, or
          - synthesise requirements if all phases are complete.
        """
        # Append user's answer to history
        # Determine what phase the last assistant msg was on
        last_phase = next((m.phase for m in reversed(history) if m.role == "assistant"), 1)
        updated_history = history + [
            ElicitationMessage(role="user", content=user_answer, phase=last_phase)
        ]

        phase_idx, q_in_phase, overall_q = _compute_phase_and_q_index(updated_history)
        progress_pct = min(int((overall_q / TOTAL_QUESTIONS) * 100), 95)

        # All phases done → synthesise
        if phase_idx >= len(PHASES):
            return await self._synthesise(idea, updated_history)

        # Generate next question
        prompt = _build_question_prompt(idea, phase_idx, q_in_phase, updated_history)
        question = await self._ask_llm(prompt)

        phase_label, phase_desc, _, _ = PHASES[phase_idx]
        next_msg = ElicitationMessage(
            role="assistant", content=question, phase=phase_idx + 1
        )

        return ElicitationChatResponse(
            question=question,
            phase=phase_idx + 1,
            phase_label=phase_label,
            phase_description=phase_desc,
            progress_pct=progress_pct,
            history=updated_history + [next_msg],
            is_complete=False,
        )

    async def _synthesise(
        self, idea: str, history: List[ElicitationMessage]
    ) -> ElicitationChatResponse:
        """Synthesise all Q&A into a formal RequirementsResponse."""
        logger.info("ElicitationService: synthesising requirements from %d messages", len(history))
        prompt = _build_synthesis_prompt(idea, history)

        for attempt in range(1, 4):
            try:
                raw = await self._ask_llm(prompt)
                parsed = _extract_json(raw)
                requirements = RequirementsResponse(**parsed)
                logger.info("ElicitationService: synthesis succeeded on attempt %d", attempt)
                return ElicitationChatResponse(
                    question="Your requirements have been synthesised from the interview. Please review and edit before proceeding.",
                    phase=len(PHASES),
                    phase_label="Synthesis Complete",
                    phase_description="Requirements extracted from your elicitation answers",
                    progress_pct=100,
                    history=history,
                    is_complete=True,
                    requirements=requirements,
                )
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                logger.warning("Synthesis attempt %d failed: %s", attempt, exc)

        raise HTTPException(
            status_code=422,
            detail="Requirements synthesis failed after 3 attempts. Please try again.",
        )

    @staticmethod
    async def _ask_llm(prompt: str) -> str:
        raw = await ollama_client.generate(prompt)
        # Strip any stray thinking tags (for models that emit them)
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        return raw.strip()

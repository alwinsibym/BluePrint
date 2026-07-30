"""Unit tests for RequirementsService – mocks app.llm.ollama_client.generate."""
import json
import pytest
from unittest.mock import AsyncMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.requirements_service import RequirementsService
from app.models.requirements import RequirementsResponse

# The import path that RequirementsService actually uses internally
PATCH_TARGET = "app.llm.ollama_client.generate"

VALID_PAYLOAD = {
    "project_name": "BudgetApp",
    "project_overview": "A personal finance tracker.",
    "objectives": ["Track expenses", "Visualise spending"],
    "functional_requirements": ["User login", "Add transactions"],
    "non_functional_requirements": ["Response < 200 ms"],
    "user_roles": ["Admin", "User"],
    "user_stories": [
        {"role": "User", "desire": "add a transaction", "benefit": "track my spending"}
    ],
    "suggested_modules": ["Auth", "Dashboard", "Reports"],
    "assumptions": ["Users have internet access"],
    "constraints": ["MVP in 3 months"],
    "recommended_tech_stack": {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "ai_framework": "Ollama",
    },
    "future_scope": ["Mobile app", "AI insights"],
}

VALID_JSON_STR = json.dumps(VALID_PAYLOAD)


def _service() -> RequirementsService:
    return RequirementsService()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_generate_requirements_success():
    """Happy path: valid JSON returned on first attempt."""
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=VALID_JSON_STR)):
        result = await svc.generate_requirements("A budgeting web app")
    assert isinstance(result, RequirementsResponse)
    assert result.project_name == "BudgetApp"
    assert len(result.objectives) == 2


@pytest.mark.asyncio
async def test_generate_requirements_strips_markdown_fences():
    """Service should strip ```json fences before parsing."""
    wrapped = f"```json\n{VALID_JSON_STR}\n```"
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=wrapped)):
        result = await svc.generate_requirements("A budgeting web app")
    assert result.project_name == "BudgetApp"


@pytest.mark.asyncio
async def test_generate_requirements_retry_then_success():
    """First attempt returns malformed JSON; second attempt succeeds."""
    responses = iter(["NOT VALID JSON", VALID_JSON_STR])

    async def side_effect(prompt: str) -> str:
        return next(responses)

    with patch(PATCH_TARGET, side_effect=side_effect):
        result = await _service().generate_requirements("A budgeting web app")
    assert result.project_name == "BudgetApp"


@pytest.mark.asyncio
async def test_generate_requirements_all_retries_exhausted():
    """When all retries fail the service raises HTTPException(422)."""
    from fastapi import HTTPException
    with patch(PATCH_TARGET, new=AsyncMock(return_value="ALWAYS BAD JSON")):
        with pytest.raises(HTTPException) as exc_info:
            await _service().generate_requirements("broken idea")
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_load_prompt_file_missing():
    """load_prompt raises FileNotFoundError for unknown prompt names."""
    from app.services.base_service import BaseService
    with pytest.raises(FileNotFoundError):
        BaseService.load_prompt("nonexistent_prompt_xyz")


@pytest.mark.asyncio
async def test_generate_requirements_respects_retry_count(monkeypatch):
    """REQUIREMENTS_AGENT_RETRY_COUNT env override is respected."""
    import app.core.config as config_module
    monkeypatch.setattr(config_module.settings, "REQUIREMENTS_AGENT_RETRY_COUNT", 1)

    call_count = 0

    async def always_bad(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        return "GARBAGE"

    from fastapi import HTTPException
    with patch(PATCH_TARGET, side_effect=always_bad):
        with pytest.raises(HTTPException):
            await _service().generate_requirements("test")
    assert call_count == 1  # only 1 attempt when retry_count=1

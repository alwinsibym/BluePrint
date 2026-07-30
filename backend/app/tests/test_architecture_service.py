import json
import pytest
from unittest.mock import AsyncMock, patch

from app.services.architecture_service import ArchitectureService
from app.models.architecture import ArchitectureResponse
from app.models.requirements import RequirementsResponse

# Reusing a mock valid requirements object
VALID_REQ_PAYLOAD = {
    "project_name": "BudgetApp",
    "project_overview": "A personal finance tracker.",
    "objectives": ["Track expenses", "Visualise spending"],
    "functional_requirements": ["User login", "Add transactions"],
    "non_functional_requirements": ["Response < 200 ms"],
    "user_roles": ["Admin", "User"],
    "user_stories": [],
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

VALID_ARCH_PAYLOAD = {
    "high_level_architecture": "Client-server architecture.",
    "folder_structure": ["src/components", "src/services"],
    "component_breakdown": [
        {"name": "Auth", "description": "Handles login", "dependencies": ["Database"]}
    ],
    "data_flow": "Client -> API -> Database"
}

VALID_ARCH_JSON_STR = json.dumps(VALID_ARCH_PAYLOAD)
PATCH_TARGET = "app.llm.ollama_client.generate"

def _service() -> ArchitectureService:
    return ArchitectureService()

@pytest.fixture
def mock_requirements() -> RequirementsResponse:
    return RequirementsResponse(**VALID_REQ_PAYLOAD)

@pytest.mark.asyncio
async def test_generate_architecture_success(mock_requirements):
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=VALID_ARCH_JSON_STR)):
        result = await svc.generate_architecture(mock_requirements)
    assert isinstance(result, ArchitectureResponse)
    assert result.high_level_architecture == "Client-server architecture."
    assert len(result.folder_structure) == 2
    assert result.component_breakdown[0].name == "Auth"

@pytest.mark.asyncio
async def test_generate_architecture_strips_markdown_fences(mock_requirements):
    wrapped = f"```json\n{VALID_ARCH_JSON_STR}\n```"
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=wrapped)):
        result = await svc.generate_architecture(mock_requirements)
    assert result.high_level_architecture == "Client-server architecture."

@pytest.mark.asyncio
async def test_generate_architecture_retry_then_success(mock_requirements):
    responses = iter(["NOT VALID JSON", VALID_ARCH_JSON_STR])
    async def side_effect(prompt: str) -> str:
        return next(responses)

    with patch(PATCH_TARGET, side_effect=side_effect):
        result = await _service().generate_architecture(mock_requirements)
    assert result.high_level_architecture == "Client-server architecture."

@pytest.mark.asyncio
async def test_generate_architecture_all_retries_exhausted(mock_requirements):
    from fastapi import HTTPException
    with patch(PATCH_TARGET, new=AsyncMock(return_value="ALWAYS BAD JSON")):
        with pytest.raises(HTTPException) as exc_info:
            await _service().generate_architecture(mock_requirements)
    assert exc_info.value.status_code == 422

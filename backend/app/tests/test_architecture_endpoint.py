import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)

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

@pytest.mark.asyncio
async def test_endpoint_returns_200_on_valid_requirements():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value=json.dumps(VALID_ARCH_PAYLOAD)),
    ):
        response = client.post(
            "/agents/architecture", json=VALID_REQ_PAYLOAD
        )
    assert response.status_code == 200
    data = response.json()
    assert data["high_level_architecture"] == "Client-server architecture."
    assert "folder_structure" in data

@pytest.mark.asyncio
async def test_endpoint_returns_422_on_malformed_llm_output():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value="THIS IS NOT JSON"),
    ):
        response = client.post(
            "/agents/architecture", json=VALID_REQ_PAYLOAD
        )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_endpoint_missing_requirements_field():
    # Sending missing fields (e.g. empty JSON) should fail Pydantic validation of RequirementsResponse
    response = client.post("/agents/architecture", json={})
    assert response.status_code == 422

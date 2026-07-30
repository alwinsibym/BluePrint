"""Integration tests for POST /agents/requirements via FastAPI TestClient."""
import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "project_name": "BudgetApp",
    "project_overview": "A personal finance tracker.",
    "objectives": ["Track expenses"],
    "functional_requirements": ["User login"],
    "non_functional_requirements": ["Fast response"],
    "user_roles": ["User"],
    "user_stories": [
        {"role": "User", "desire": "see charts", "benefit": "understand spending"}
    ],
    "suggested_modules": ["Auth"],
    "assumptions": ["Internet access"],
    "constraints": ["3-month MVP"],
    "recommended_tech_stack": {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "ai_framework": "Ollama",
    },
    "future_scope": ["Mobile app"],
}


@pytest.mark.asyncio
async def test_endpoint_returns_200_on_valid_idea():
    """POST /agents/requirements with a valid idea returns 200 and correct schema."""
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value=json.dumps(VALID_PAYLOAD)),
    ):
        response = client.post(
            "/agents/requirements", json={"idea": "A budgeting web app"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "BudgetApp"
    assert "functional_requirements" in data
    assert "recommended_tech_stack" in data
    assert data["recommended_tech_stack"]["frontend"] == "React"


@pytest.mark.asyncio
async def test_endpoint_returns_422_on_empty_idea():
    """POST with an empty idea string — service retries with empty prompt and gets 422 after exhausted retries."""
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value="NOT JSON"),
    ):
        response = client.post("/agents/requirements", json={"idea": ""})
    # Either Pydantic rejects it (422) or the service exhausts retries (422)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_endpoint_returns_422_on_malformed_llm_output():
    """When the LLM always returns malformed JSON, the endpoint returns 422."""
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value="THIS IS NOT JSON"),
    ):
        response = client.post(
            "/agents/requirements", json={"idea": "A project"}
        )
    assert response.status_code == 422


def test_endpoint_missing_idea_field():
    """POST without the 'idea' field returns 422 (Pydantic required field)."""
    response = client.post("/agents/requirements", json={})
    assert response.status_code == 422

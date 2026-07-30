import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)

VALID_CONTEXT_PAYLOAD = {
    "requirements": {
        "project_name": "BudgetApp",
        "project_overview": "A personal finance tracker.",
        "objectives": ["Track expenses"],
        "functional_requirements": ["User login"],
        "non_functional_requirements": ["Response < 200 ms"],
        "user_roles": ["User"],
        "user_stories": [],
        "suggested_modules": ["Auth"],
        "assumptions": ["Users have internet access"],
        "constraints": ["MVP in 3 months"],
        "recommended_tech_stack": {
            "frontend": "React",
            "backend": "FastAPI",
            "database": "SQLite",
            "ai_framework": "Ollama",
        },
        "future_scope": ["Mobile app"],
    },
    "architecture": {
        "high_level_architecture": "Client-server architecture.",
        "folder_structure": ["src/components"],
        "component_breakdown": [
            {"name": "Auth", "description": "Handles login", "dependencies": ["Database"]}
        ],
        "data_flow": "Client -> API -> Database"
    },
    "database": {
        "database_overview": "SQLite database.",
        "entities": [
            {
                "name": "users",
                "description": "Users table",
                "attributes": ["id INTEGER PRIMARY KEY"],
                "primary_key": "id",
                "foreign_keys": []
            }
        ],
        "relationships": ["User 1:N Transactions"],
        "normalization_notes": "3NF",
        "table_summary": "Created users.",
        "sql_schema": "CREATE TABLE users (id INTEGER PRIMARY KEY);",
        "mermaid_er_diagram": "erDiagram\n  USERS"
    }
}

VALID_DOC_PAYLOAD = {
    "project_overview": "# Project Overview\nBudgetApp overview.",
    "readme_md": "# BudgetApp\n\n## Description\nA finance tracker.",
    "installation_guide": "## Setup\n1. git clone\n2. npm install",
    "api_documentation": "## API Specs\n`POST /agents/requirements`",
    "folder_structure_description": "## Folder Structure\nfrontend/ and backend/",
    "deployment_notes": "## Deployment\nOllama setup guide.",
    "developer_notes": "## Developer Notes\nAssumptions and conventions."
}

@pytest.mark.asyncio
async def test_endpoint_returns_200_on_valid_context():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value=json.dumps(VALID_DOC_PAYLOAD)),
    ):
        response = client.post(
            "/agents/documentation", json=VALID_CONTEXT_PAYLOAD
        )
    assert response.status_code == 200
    data = response.json()
    assert "# BudgetApp" in data["readme_md"]
    assert "git clone" in data["installation_guide"]
    assert "POST /agents/requirements" in data["api_documentation"]

@pytest.mark.asyncio
async def test_endpoint_returns_422_on_malformed_llm_output():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value="THIS IS NOT JSON"),
    ):
        response = client.post(
            "/agents/documentation", json=VALID_CONTEXT_PAYLOAD
        )
    assert response.status_code == 422

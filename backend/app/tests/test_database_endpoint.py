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
        "functional_requirements": ["User login", "Add transactions"],
        "non_functional_requirements": ["Response < 200 ms"],
        "user_roles": ["User"],
        "user_stories": [],
        "suggested_modules": ["Auth", "Transactions"],
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
    }
}

VALID_DB_PAYLOAD = {
    "database_overview": "SQLite database for finance tracking.",
    "entities": [
        {
            "name": "users",
            "description": "User account info",
            "attributes": ["id INTEGER PRIMARY KEY", "email TEXT"],
            "primary_key": "id",
            "foreign_keys": []
        }
    ],
    "relationships": ["User 1:N Transactions"],
    "normalization_notes": "Normalized to 3NF.",
    "table_summary": "Created users table.",
    "sql_schema": "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT);",
    "mermaid_er_diagram": "erDiagram\n  USERS ||--o{ TRANSACTIONS : places"
}

@pytest.mark.asyncio
async def test_endpoint_returns_200_on_valid_context():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value=json.dumps(VALID_DB_PAYLOAD)),
    ):
        response = client.post(
            "/agents/database", json=VALID_CONTEXT_PAYLOAD
        )
    assert response.status_code == 200
    data = response.json()
    assert data["database_overview"] == "SQLite database for finance tracking."
    assert "sql_schema" in data
    assert "mermaid_er_diagram" in data

@pytest.mark.asyncio
async def test_endpoint_returns_422_on_malformed_llm_output():
    with patch(
        "app.llm.ollama_client.generate",
        new=AsyncMock(return_value="THIS IS NOT JSON"),
    ):
        response = client.post(
            "/agents/database", json=VALID_CONTEXT_PAYLOAD
        )
    assert response.status_code == 422

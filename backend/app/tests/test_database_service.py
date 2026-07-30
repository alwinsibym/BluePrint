import json
import pytest
from unittest.mock import AsyncMock, patch

from app.services.database_service import DatabaseService
from app.models.database import DatabaseResponse
from app.models.requirements import ProjectContext, RequirementsResponse
from app.models.architecture import ArchitectureResponse

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

VALID_DB_JSON_STR = json.dumps(VALID_DB_PAYLOAD)
PATCH_TARGET = "app.llm.ollama_client.generate"

def _service() -> DatabaseService:
    return DatabaseService()

@pytest.fixture
def mock_context() -> ProjectContext:
    return ProjectContext(**VALID_CONTEXT_PAYLOAD)

@pytest.mark.asyncio
async def test_generate_database_success(mock_context):
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=VALID_DB_JSON_STR)):
        result = await svc.generate_database(mock_context)
    assert isinstance(result, DatabaseResponse)
    assert result.database_overview == "SQLite database for finance tracking."
    assert len(result.entities) == 1
    assert result.entities[0].name == "users"

@pytest.mark.asyncio
async def test_generate_database_strips_markdown_fences(mock_context):
    wrapped = f"```json\n{VALID_DB_JSON_STR}\n```"
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=wrapped)):
        result = await svc.generate_database(mock_context)
    assert result.entities[0].name == "users"

@pytest.mark.asyncio
async def test_generate_database_all_retries_exhausted(mock_context):
    from fastapi import HTTPException
    with patch(PATCH_TARGET, new=AsyncMock(return_value="ALWAYS BAD JSON")):
        with pytest.raises(HTTPException) as exc_info:
            await _service().generate_database(mock_context)
    assert exc_info.value.status_code == 422

import json
import pytest
from unittest.mock import AsyncMock, patch

from app.services.documentation_service import DocumentationService
from app.models.documentation import DocumentationResponse
from app.models.requirements import ProjectContext

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

VALID_DOC_JSON_STR = json.dumps(VALID_DOC_PAYLOAD)
PATCH_TARGET = "app.llm.ollama_client.generate"

def _service() -> DocumentationService:
    return DocumentationService()

@pytest.fixture
def mock_context() -> ProjectContext:
    return ProjectContext(**VALID_CONTEXT_PAYLOAD)

@pytest.mark.asyncio
async def test_generate_documentation_success(mock_context):
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=VALID_DOC_JSON_STR)):
        result = await svc.generate_documentation(mock_context)
    assert isinstance(result, DocumentationResponse)
    assert "BudgetApp overview" in result.project_overview
    assert "# BudgetApp" in result.readme_md
    assert "git clone" in result.installation_guide
    assert "POST /agents/requirements" in result.api_documentation
    assert "frontend/" in result.folder_structure_description
    assert "Ollama setup" in result.deployment_notes
    assert "Assumptions" in result.developer_notes

@pytest.mark.asyncio
async def test_generate_documentation_strips_markdown_fences(mock_context):
    wrapped = f"```json\n{VALID_DOC_JSON_STR}\n```"
    svc = _service()
    with patch(PATCH_TARGET, new=AsyncMock(return_value=wrapped)):
        result = await svc.generate_documentation(mock_context)
    assert "# BudgetApp" in result.readme_md

@pytest.mark.asyncio
async def test_generate_documentation_all_retries_exhausted(mock_context):
    from fastapi import HTTPException
    with patch(PATCH_TARGET, new=AsyncMock(return_value="ALWAYS BAD JSON")):
        with pytest.raises(HTTPException) as exc_info:
            await _service().generate_documentation(mock_context)
    assert exc_info.value.status_code == 422

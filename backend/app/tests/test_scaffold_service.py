"""
Tests – Scaffold Service (Phase 7)
-----------------------------------
Unit tests for the Phase 7 pipeline:
  ScaffoldService → ScaffoldAgent → ProjectGeneratorBuilder → ScaffoldResponse
"""

import pytest
from app.models.architecture import ArchitectureComponent, ArchitectureResponse
from app.models.database import DatabaseResponse, Entity
from app.models.documentation import DocumentationResponse
from app.models.requirements import (
    ProjectContext,
    RecommendedTechStack,
    RequirementsResponse,
    UserStory,
)
from app.services.scaffold_service import ScaffoldService


@pytest.fixture
def full_context() -> ProjectContext:
    req = RequirementsResponse(
        project_name="TaskFlow",
        project_overview="A task management application.",
        objectives=["Manage tasks", "Authenticate users"],
        functional_requirements=["Create task", "Delete task"],
        non_functional_requirements=["Response < 200ms"],
        user_roles=["Admin", "User"],
        user_stories=[UserStory(role="User", desire="create tasks", benefit="stay organised")],
        suggested_modules=["tasks", "users", "auth"],
        assumptions=["SQLite is sufficient"],
        constraints=["No cloud required"],
        recommended_tech_stack=RecommendedTechStack(
            frontend="React",
            backend="FastAPI",
            database="SQLite",
            ai_framework="Ollama",
        ),
        future_scope=["Add notifications"],
    )

    arch = ArchitectureResponse(
        high_level_architecture="React SPA + FastAPI REST + SQLite",
        folder_structure=["backend/", "frontend/", "database/"],
        component_breakdown=[
            ArchitectureComponent(name="TaskRouter", description="Handles task CRUD", dependencies=[]),
            ArchitectureComponent(name="UserRouter", description="Handles user management", dependencies=[]),
        ],
        data_flow="User → Frontend → FastAPI → SQLite",
    )

    db = DatabaseResponse(
        database_overview="SQLite database with tasks and users tables.",
        entities=[
            Entity(
                name="Task",
                description="Represents a user task.",
                attributes=["id INTEGER PRIMARY KEY", "title TEXT NOT NULL", "done BOOLEAN"],
                primary_key="id",
                foreign_keys=["user_id REFERENCES users(id)"],
            ),
            Entity(
                name="User",
                description="App user.",
                attributes=["id INTEGER PRIMARY KEY", "email TEXT UNIQUE", "password TEXT"],
                primary_key="id",
                foreign_keys=[],
            ),
        ],
        relationships=["User 1:N Task"],
        normalization_notes="3NF",
        table_summary="2 tables: tasks, users",
        sql_schema="CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL);\nCREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE);",
        mermaid_er_diagram="erDiagram\n  USER ||--o{ TASK : owns",
    )

    doc = DocumentationResponse(
        project_overview="TaskFlow – a task management application.",
        readme_md="# TaskFlow\nA task management app built with Blueprint.",
        installation_guide="## Setup\n1. pip install -r requirements.txt\n2. npm install\n3. Run the app.",
        api_documentation="## API\nPOST /tasks, GET /tasks",
        folder_structure_description="backend/ contains FastAPI code, frontend/ contains React.",
        deployment_notes="Deploy on any Python 3.12 host.",
        developer_notes="Use SQLite for local development.",
    )

    return ProjectContext(
        requirements=req,
        architecture=arch,
        database=db,
        documentation=doc,
    )


@pytest.fixture
def minimal_context() -> ProjectContext:
    return ProjectContext()


@pytest.mark.asyncio
async def test_scaffold_generates_files(full_context: ProjectContext):
    """Full context should produce a ScaffoldResponse with multiple files."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)

    assert result.project_name == "TaskFlow"
    assert result.total_files > 0
    assert len(result.files) == result.total_files
    assert result.tree_view  # non-empty ASCII tree
    assert result.generation_summary


@pytest.mark.asyncio
async def test_required_files_present(full_context: ProjectContext):
    """Key files should always be present in the scaffold output."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)
    paths = {f.path for f in result.files}

    for required in [
        "README.md",
        "backend/app/main.py",
        "frontend/src/App.tsx",
        "database/schema.sql",
        "generated/project_summary.json",
        "generated/generation_report.md",
        ".gitignore",
        ".env.example",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        ".github/workflows/ci.yml",
    ]:
        assert required in paths, f"Missing expected file: {required}"


@pytest.mark.asyncio
async def test_sql_schema_included(full_context: ProjectContext):
    """The database/schema.sql should contain the SQL from DatabaseResponse."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)
    schema_file = next((f for f in result.files if f.path == "database/schema.sql"), None)
    assert schema_file is not None
    assert "CREATE TABLE" in schema_file.content


@pytest.mark.asyncio
async def test_readme_uses_documentation_agent(full_context: ProjectContext):
    """README.md content should come from DocumentationResponse.readme_md."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)
    readme = next((f for f in result.files if f.path == "README.md"), None)
    assert readme is not None
    assert "TaskFlow" in readme.content


@pytest.mark.asyncio
async def test_minimal_context_still_generates(minimal_context: ProjectContext):
    """Even with an empty context, the scaffold should not crash."""
    service = ScaffoldService()
    result = await service.generate_scaffold(minimal_context)
    assert result.total_files > 0


@pytest.mark.asyncio
async def test_generation_report_present(full_context: ProjectContext):
    """A generation_report.md should always be appended."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)
    report = next((f for f in result.files if f.path == "generated/generation_report.md"), None)
    assert report is not None
    assert "Blueprint Generation Report" in report.content


@pytest.mark.asyncio
async def test_entity_router_stubs(full_context: ProjectContext):
    """Entity router files should be created for each entity."""
    service = ScaffoldService()
    result = await service.generate_scaffold(full_context)
    paths = {f.path for f in result.files}
    # Entities: Task → task_router.py, User → user_router.py
    assert "backend/app/api/task_router.py" in paths
    assert "backend/app/api/user_router.py" in paths

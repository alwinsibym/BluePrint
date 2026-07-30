import io
import json
import zipfile
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

REQ_PAYLOAD = {
    "project_name": "Trailhead",
    "project_overview": "A social hiking log app where users track completed trails and share photos.",
    "objectives": ["Track trails", "Share photos"],
    "functional_requirements": ["User authentication", "Trail logging"],
    "non_functional_requirements": ["High availability", "Fast search"],
    "user_roles": ["Hiker", "Admin"],
    "user_stories": [{"role": "Hiker", "desire": "log a completed trail", "benefit": "keep a history of hikes"}],
    "suggested_modules": ["Auth", "Trails", "Photos"],
    "assumptions": ["GPS access available"],
    "constraints": ["Mobile responsive"],
    "recommended_tech_stack": {
        "frontend": "React",
        "backend": "FastAPI",
        "database": "SQLite",
        "ai_framework": "Ollama",
    },
    "future_scope": ["Offline maps"],
}

ARCH_PAYLOAD = {
    "high_level_architecture": "Layered micro-monolith with React frontend and FastAPI backend.",
    "folder_structure": ["frontend/src", "backend/app", "docs"],
    "component_breakdown": [
        {"name": "AuthService", "description": "Handles JWT authentication", "dependencies": ["Database"]},
        {"name": "TrailService", "description": "Manages trail records", "dependencies": ["Database"]},
    ],
    "data_flow": "React -> FastAPI REST API -> SQLite Database",
}

DB_PAYLOAD = {
    "database_overview": "Relational SQLite database designed with 3NF normalization.",
    "entities": [
        {
            "name": "users",
            "description": "Registered hikers",
            "attributes": ["id INT", "email VARCHAR", "password_hash VARCHAR"],
            "primary_key": "id",
            "foreign_keys": [],
        },
        {
            "name": "trails",
            "description": "Logged hiking trails",
            "attributes": ["id INT", "user_id INT", "title VARCHAR", "distance FLOAT"],
            "primary_key": "id",
            "foreign_keys": ["user_id REFERENCES users(id)"],
        },
    ],
    "relationships": ["users 1:N trails"],
    "normalization_notes": "Normalized up to 3NF",
    "table_summary": "2 tables: users, trails",
    "sql_schema": "CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT);\nCREATE TABLE trails (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT);",
    "mermaid_er_diagram": "erDiagram\n  users ||--o{ trails : logs",
}

DOCS_PAYLOAD = {
    "project_overview": "Trailhead - Social Hiking Log Platform.",
    "readme_md": "# Trailhead\n\nSocial hiking log platform.\n\n## Getting Started\n\nRun backend and frontend.",
    "installation_guide": "1. Install requirements\n2. Run backend\n3. Run frontend",
    "api_documentation": "GET /api/v1/trails\nPOST /api/v1/trails",
    "folder_structure_description": "Standard React + FastAPI layout",
    "deployment_notes": "Deploy using Docker or standard Uvicorn server",
    "developer_notes": "Maintain clean modular routers.",
}

@patch("app.llm.ollama_client.generate", new_callable=AsyncMock)
def test_full_pipeline_simulation(mock_generate):
    """Simulates the full end-to-end multi-agent pipeline:
    1. Requirements Agent (POST /agents/requirements)
    2. Architecture Agent (POST /agents/architecture)
    3. Database Agent (POST /agents/database)
    4. Documentation Agent (POST /agents/documentation)
    5. Scaffold Agent / Project Generator (POST /agents/scaffold)
    6. ZIP Export (POST /agents/scaffold/export-zip)
    """
    
    # Configure mock responses for sequentially called agents
    mock_generate.side_effect = [
        json.dumps(REQ_PAYLOAD),
        json.dumps(ARCH_PAYLOAD),
        json.dumps(DB_PAYLOAD),
        json.dumps(DOCS_PAYLOAD),
    ]

    # --- Step 1: Requirements Agent ---
    req_res = client.post("/agents/requirements", json={"idea": "Trailhead hiking app"})
    assert req_res.status_code == 200, f"Requirements failed: {req_res.text}"
    req_data = req_res.json()
    assert req_data["project_name"] == "Trailhead"

    # --- Step 2: Architecture Agent ---
    arch_res = client.post("/agents/architecture", json=req_data)
    assert arch_res.status_code == 200, f"Architecture failed: {arch_res.text}"
    arch_data = arch_res.json()
    assert "high_level_architecture" in arch_data

    # --- Step 3: Database Agent ---
    db_context = {
        "requirements": req_data,
        "architecture": arch_data,
        "database": None,
        "documentation": None,
    }
    db_res = client.post("/agents/database", json=db_context)
    assert db_res.status_code == 200, f"Database failed: {db_res.text}"
    db_data = db_res.json()
    assert len(db_data["entities"]) == 2

    # --- Step 4: Documentation Agent ---
    docs_context = {
        "requirements": req_data,
        "architecture": arch_data,
        "database": db_data,
        "documentation": None,
    }
    docs_res = client.post("/agents/documentation", json=docs_context)
    assert docs_res.status_code == 200, f"Documentation failed: {docs_res.text}"
    docs_data = docs_res.json()
    assert "# Trailhead" in docs_data["readme_md"]

    # --- Step 5: Scaffold Agent / Deterministic Project Generator ---
    full_context = {
        "requirements": req_data,
        "architecture": arch_data,
        "database": db_data,
        "documentation": docs_data,
    }
    scaffold_res = client.post("/agents/scaffold", json=full_context)
    assert scaffold_res.status_code == 200, f"Scaffold failed: {scaffold_res.text}"
    scaffold_data = scaffold_res.json()
    assert scaffold_data["total_files"] >= 20
    assert any(f["path"] == "README.md" for f in scaffold_data["files"])
    assert any("schema.sql" in f["path"] for f in scaffold_data["files"])

    # --- Step 6: ZIP Export Service ---
    zip_res = client.post("/agents/scaffold/export-zip", json=scaffold_data)
    assert zip_res.status_code == 200, f"ZIP Export failed: {zip_res.text}"
    assert zip_res.headers["content-type"] == "application/zip"
    
    # Read the returned stream as zip
    zip_bytes = zip_res.content
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "README.md" in namelist
        assert "database/schema.sql" in namelist

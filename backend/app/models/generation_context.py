"""
Generation Context Model
------------------------
Defines the structured metadata that the Scaffold Agent produces and that the
Project Generator consumes.

This model acts as the **contract** between the AI planning layer and the
deterministic project‑generation layer:

* AI agents decide **what** should exist  →  GenerationContext
* Project Generator decides **how** it is built  →  rendered files / folders
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ApiRoute(BaseModel):
    path: str = Field(..., description="URL path, e.g. '/items'")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET"
    handler_name: str = Field(..., description="Python function name for the handler")
    description: str = ""


class Entity(BaseModel):
    name: str = Field(..., description="Entity / table name, e.g. 'User'")
    attributes: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of {name, type} dicts, e.g. [{name: 'email', type: 'str'}]",
    )
    relationships: List[str] = Field(
        default_factory=list,
        description="Human‑readable relationship descriptions",
    )


class GenerationContext(BaseModel):
    """Structured metadata produced by the Scaffold Agent.

    The Project Generator maps every field in this model to the appropriate
    template variables when rendering the project skeleton.
    """

    project_name: str = Field(..., description="Human‑readable project name")
    project_name_slug: str = Field(..., description="Lowercase, hyphenated slug for package names")
    frontend_type: Literal["react", "nextjs", "vue", "angular"] = Field(
        "react", description="Frontend framework"
    )
    backend_type: Literal["fastapi", "django", "express"] = Field(
        "fastapi", description="Backend framework"
    )
    database_type: Literal["sqlite", "postgres", "mysql"] = Field(
        "sqlite", description="Database engine"
    )
    authentication: Literal["jwt", "oauth2", "none"] = Field(
        "none", description="Authentication strategy"
    )
    api_routes: List[ApiRoute] = Field(
        default_factory=list, description="List of backend API routes to stub"
    )
    entities: List[Entity] = Field(
        default_factory=list, description="Domain entities / data models"
    )
    modules: List[str] = Field(
        default_factory=list, description="High‑level backend module names"
    )
    documentation_files: List[str] = Field(
        default_factory=list, description="Docs markdown filenames to generate"
    )
    folder_structure: Dict[str, Any] = Field(
        default_factory=dict, description="Nested dict describing the folder/file tree"
    )
    configuration: Dict[str, Any] = Field(
        default_factory=dict, description="Env vars, settings, pyproject fields, etc."
    )
    sql_schema: Optional[str] = Field(None, description="Raw SQL DDL for schema.sql")
    readme_content: Optional[str] = Field(None, description="Pre‑generated README.md body")
    architecture_summary: Optional[str] = Field(None, description="Architecture summary text")

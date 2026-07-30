"""
Scaffold Agent
--------------
The final AI‑layer agent.  It reads the accumulated ``ProjectContext`` and
**produces a ``GenerationContext``** – structured metadata that completely
describes what the generated project should contain.

The Scaffold Agent does NOT write any files.
All file creation is delegated to the deterministic ``ProjectGeneratorBuilder``.

Flow
~~~~
ProjectContext  →  ScaffoldAgent.handle()  →  GenerationContext
GenerationContext  →  ProjectGeneratorBuilder.build()  →  ScaffoldResponse
"""

from __future__ import annotations

import re
import time

from app.agents.base_agent import BaseAgent
from app.context_manager import AgentMetadata, ProjectContextManager
from app.models.generation_context import ApiRoute
from app.models.generation_context import Entity as GenEntity
from app.models.generation_context import GenerationContext
from app.models.requirements import ProjectContext
from app.models.scaffold import ScaffoldResponse
from app.project_generator.builder import ProjectGeneratorBuilder


class ScaffoldAgent(BaseAgent):
    """Converts the accumulated ``ProjectContext`` into a ``ScaffoldResponse``.

    Responsibilities
    ~~~~~~~~~~~~~~~~
    1. Derive ``GenerationContext`` metadata from ``ProjectContext`` (no LLM call).
    2. Delegate file generation to ``ProjectGeneratorBuilder`` (deterministic).
    3. Record agent metadata (timing, tokens estimate) in ``ProjectContextManager``.
    """

    def __init__(self) -> None:
        self._ctx_manager = ProjectContextManager()
        self._builder = ProjectGeneratorBuilder()

    async def handle(self, context: ProjectContext) -> ScaffoldResponse:  # type: ignore[override]
        t0 = time.monotonic()

        gen_ctx = self._build_generation_context(context)
        response = self._builder.build(gen_ctx)

        elapsed = f"{time.monotonic() - t0:.1f}s"
        meta = AgentMetadata(
            agent="Scaffold Agent",
            status="Completed",
            execution_time=elapsed,
            tokens=0,  # deterministic – no LLM tokens used
        )
        self._ctx_manager.record_metadata(meta)
        self._ctx_manager.update_section("scaffold", response.model_dump())

        return response

    # ------------------------------------------------------------------
    # GenerationContext construction
    # ------------------------------------------------------------------

    def _build_generation_context(self, ctx: ProjectContext) -> GenerationContext:
        req = ctx.requirements
        arch = ctx.architecture
        db = ctx.database

        project_name = req.project_name if req else "BlueprintApp"
        slug = self._slugify(project_name)

        frontend_type = "react"
        backend_type = "fastapi"
        database_type = "sqlite"

        if req and req.recommended_tech_stack:
            fe = req.recommended_tech_stack.frontend.lower()
            be = req.recommended_tech_stack.backend.lower()
            db_tech = req.recommended_tech_stack.database.lower()
            if "next" in fe:
                frontend_type = "nextjs"
            elif "vue" in fe:
                frontend_type = "vue"
            if "django" in be:
                backend_type = "django"
            if "postgres" in db_tech or "postgresql" in db_tech:
                database_type = "postgres"
            elif "mysql" in db_tech:
                database_type = "mysql"

        # Build entities from DatabaseResponse
        entities: list[GenEntity] = []
        if db and db.entities:
            for ent in db.entities:
                # ent.attributes is List[str] like ["id INTEGER PRIMARY KEY", "name TEXT"]
                attrs = []
                for attr_str in ent.attributes:
                    parts = attr_str.strip().split()
                    if parts:
                        attrs.append({"name": parts[0], "type": " ".join(parts[1:]) or "TEXT"})
                entities.append(GenEntity(name=ent.name, attributes=attrs))

        # Build API routes from ArchitectureResponse component_breakdown
        api_routes: list[ApiRoute] = []
        if arch and arch.component_breakdown:
            for comp in arch.component_breakdown[:8]:  # cap at 8 for scaffold
                slug = self._slugify(comp.name)
                api_routes.append(ApiRoute(
                    path=f"/{slug}",
                    method="GET",
                    handler_name=f"get_{slug.replace('-', '_')}",
                    description=comp.description,
                ))

        modules = req.suggested_modules if req else []

        return GenerationContext(
            project_name=project_name,
            project_name_slug=slug,
            frontend_type=frontend_type,  # type: ignore[arg-type]
            backend_type=backend_type,    # type: ignore[arg-type]
            database_type=database_type,  # type: ignore[arg-type]
            authentication="jwt" if req and any("auth" in o.lower() for o in req.objectives) else "none",
            api_routes=api_routes,
            entities=entities,
            modules=modules,
            documentation_files=["requirements.md", "architecture.md", "database.md", "api.md"],
            sql_schema=db.sql_schema if db else None,
            readme_content=ctx.documentation.readme_md if ctx.documentation else None,
            architecture_summary=arch.high_level_architecture if arch else None,
            configuration={"database_url": "sqlite:///./app.db", "debug": True},
        )

    @staticmethod
    def _slugify(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

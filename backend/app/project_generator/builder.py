"""
Project Generator – Builder (Orchestrator)
------------------------------------------
The public API of the **Project Generator** package.

Call ``ProjectGeneratorBuilder.build(generation_context)`` and get back a
complete ``ScaffoldResponse`` with:

* All rendered files (``List[ScaffoldFile]``)
* An ASCII tree view
* A generation summary string
* A generation report (``generation_report.md`` content)
* Validation warnings

This module is the only import consumers need from ``project_generator``.

Design philosophy
~~~~~~~~~~~~~~~~~
* AI agents produce ``GenerationContext`` (the *what*)
* ``ProjectGeneratorBuilder`` deterministically produces files (the *how*)
* No LLM calls happen here – pure Python + templates
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.models.generation_context import GenerationContext
from app.models.scaffold import ScaffoldFile, ScaffoldResponse
from app.project_generator.file_generator import FileGenerator
from app.project_generator.validator import GenerationValidator


class ProjectGeneratorBuilder:
    """Orchestrates the full generation pipeline.

    Usage::

        builder = ProjectGeneratorBuilder()
        response = builder.build(generation_context)
    """

    def __init__(self) -> None:
        self._file_gen = FileGenerator()
        self._validator = GenerationValidator()

    def build(self, ctx: GenerationContext) -> ScaffoldResponse:
        """Generate the full project skeleton from a ``GenerationContext``.

        Steps
        ~~~~~
        1. ``FileGenerator`` renders all files from templates.
        2. ``GenerationValidator`` runs sanity checks.
        3. ASCII tree view is assembled.
        4. Generation report Markdown is created and appended to the file list.
        5. A ``ScaffoldResponse`` is returned.
        """
        # Step 1 – generate files
        files = self._file_gen.generate(ctx)

        # Step 2 – validate
        ok, warnings = self._validator.validate(files)

        # Step 3 – build tree
        tree_view = self._build_tree(ctx, files)

        # Step 4 – generation report
        report_md = self._build_report(ctx, files, warnings)
        files.append(ScaffoldFile(
            path="generated/generation_report.md",
            content=report_md,
            language="markdown",
            generated_by="ScaffoldAgent (Project Generator)",
        ))

        # Step 5 – summary string
        warn_str = f"  ⚠ {len(warnings)} warning(s) detected." if warnings else "  ✅ All checks passed."
        summary = (
            f"Successfully generated '{ctx.project_name}' – "
            f"{ctx.backend_type.capitalize()} backend + {ctx.frontend_type.capitalize()} frontend "
            f"+ {ctx.database_type.upper()} database. "
            f"{len(files)} files assembled.{warn_str}"
        )

        return ScaffoldResponse(
            project_name=ctx.project_name,
            tree_view=tree_view,
            files=files,
            total_files=len(files),
            generation_summary=summary,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_tree(ctx: GenerationContext, files: List[ScaffoldFile]) -> str:
        """Build a readable ASCII directory tree from the file paths."""
        lines = [f"{ctx.project_name}/"]

        # Group by top‑level dir for a clean display
        top_dirs: dict = {}
        for f in files:
            parts = f.path.split("/")
            top = parts[0]
            if len(parts) == 1:
                top_dirs.setdefault("__root__", []).append(parts[0])
            else:
                top_dirs.setdefault(top, []).append("/".join(parts[1:]))

        root_files = top_dirs.pop("__root__", [])
        for rf in root_files:
            lines.append(f"├── {rf}")

        dir_keys = sorted(top_dirs.keys())
        for i, dir_name in enumerate(dir_keys):
            connector = "└──" if i == len(dir_keys) - 1 else "├──"
            lines.append(f"{connector} {dir_name}/")
            sub_files = sorted(top_dirs[dir_name])
            for j, sub in enumerate(sub_files):
                sub_conn = "    └──" if j == len(sub_files) - 1 else "    ├──"
                lines.append(f"{sub_conn} {sub}")

        return "\n".join(lines)

    @staticmethod
    def _build_report(
        ctx: GenerationContext,
        files: List[ScaffoldFile],
        warnings: List[str],
    ) -> str:
        """Produce the human‑readable generation report markdown."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        agents = ["Requirements", "Architecture", "Database", "Documentation", "Scaffold"]
        agent_lines = "\n".join(f"- ✅ {a} Agent" for a in agents)
        warning_lines = "\n".join(f"- ⚠ {w}" for w in warnings) if warnings else "- None"
        entity_lines = "\n".join(f"- {e.name}" for e in ctx.entities) if ctx.entities else "- None defined"
        route_lines = "\n".join(f"- `{r.method} {r.path}` – {r.description}" for r in ctx.api_routes) if ctx.api_routes else "- None defined"

        return f"""# Blueprint Generation Report

## Project Overview

| Field | Value |
|-------|-------|
| **Project Name** | {ctx.project_name} |
| **Generated On** | {now} |
| **Frontend** | {ctx.frontend_type.capitalize()} |
| **Backend** | {ctx.backend_type.capitalize()} |
| **Database** | {ctx.database_type.upper()} |
| **Authentication** | {ctx.authentication.upper()} |
| **Total Files Generated** | {len(files)} |

## Completed Agents

{agent_lines}

## Domain Entities

{entity_lines}

## API Routes

{route_lines}

## Validation Warnings

{warning_lines}

## Notes

- This project was scaffolded by **Blueprint** – an AI‑assisted Software Planning & Project Assembly Platform.
- The Scaffold Agent produced the Generation Context; the Project Generator rendered all files deterministically.
- No LLM calls were made during file generation.
"""

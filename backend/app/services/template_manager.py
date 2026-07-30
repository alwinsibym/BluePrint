import json
from pathlib import Path
from typing import List
from app.models.requirements import ProjectContext
from app.models.scaffold import ScaffoldFile

class TemplateManager:
    """Loads templates from disk, substitutes variables from ProjectContext,
    and assembles the complete file tree for the scaffolded project foundation.
    """

    def __init__(self) -> None:
        self.templates_dir = Path(__file__).resolve().parent.parent / "templates"

    def _read_template(self, template_filename: str) -> str:
        filepath = self.templates_dir / template_filename
        if not filepath.is_file():
            raise FileNotFoundError(f"Template file not found: {filepath}")
        return filepath.read_text(encoding="utf-8")

    def _substitute(self, template_str: str, replacements: dict) -> str:
        result = template_str
        for key, val in replacements.items():
            result = result.replace(f"{{{{{key}}}}}", str(val))
        return result

    def assemble_scaffold(self, context: ProjectContext) -> tuple[str, List[ScaffoldFile]]:
        """Assembles all files from templates and context, returning (tree_view, files)."""
        req = context.requirements
        arch = context.architecture
        db = context.database
        doc = context.documentation

        project_name = req.project_name if req else "BlueprintApp"
        project_overview = req.project_overview if req else "A software project built with Blueprint."
        ai_framework = req.recommended_tech_stack.ai_framework if req else "Ollama"
        project_name_lower = project_name.lower().replace(" ", "-")

        replacements = {
            "project_name": project_name,
            "project_name_lowercase": project_name_lower,
            "project_overview": project_overview,
            "ai_framework": ai_framework,
        }

        files: List[ScaffoldFile] = []

        # 1. Root Files
        readme_content = doc.readme_md if doc else f"# {project_name}\n\n{project_overview}"
        files.append(ScaffoldFile(
            path="README.md",
            content=readme_content,
            language="markdown",
            generated_by="DocumentationAgent"
        ))

        license_str = self._substitute(self._read_template("license.template"), replacements)
        files.append(ScaffoldFile(
            path="LICENSE",
            content=license_str,
            language="text",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        gitignore_str = self._read_template("gitignore.template")
        files.append(ScaffoldFile(
            path=".gitignore",
            content=gitignore_str,
            language="text",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        env_str = self._substitute(self._read_template("env.example.template"), replacements)
        files.append(ScaffoldFile(
            path=".env.example",
            content=env_str,
            language="text",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        # 2. Documentation Folder
        if req:
            files.append(ScaffoldFile(
                path="docs/requirements.md",
                content=f"# Requirements Specification\n\n**Overview:** {req.project_overview}\n\n## Objectives\n" + "\n".join(f"- {o}" for o in req.objectives),
                language="markdown",
                generated_by="RequirementsAgent"
            ))

        if arch:
            files.append(ScaffoldFile(
                path="docs/architecture.md",
                content=f"# Software Architecture\n\n{arch.high_level_architecture}\n\n## Data Flow\n{arch.data_flow}",
                language="markdown",
                generated_by="ArchitectureAgent"
            ))

        if db:
            files.append(ScaffoldFile(
                path="docs/database.md",
                content=f"# Database Documentation\n\n{db.database_overview}\n\n## Normalization Notes\n{db.normalization_notes}",
                language="markdown",
                generated_by="DatabaseAgent"
            ))

        # 3. Backend Folder
        fastapi_main = self._substitute(self._read_template("fastapi_main.py.template"), replacements)
        files.append(ScaffoldFile(
            path="backend/app/main.py",
            content=fastapi_main,
            language="python",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        fastapi_db = self._read_template("fastapi_database.py.template")
        files.append(ScaffoldFile(
            path="backend/app/database.py",
            content=fastapi_db,
            language="python",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        req_txt = self._read_template("requirements.txt.template")
        files.append(ScaffoldFile(
            path="backend/requirements.txt",
            content=req_txt,
            language="text",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        # 4. Frontend Folder
        react_app = self._substitute(self._read_template("react_app.tsx.template"), replacements)
        files.append(ScaffoldFile(
            path="frontend/src/App.tsx",
            content=react_app,
            language="typescript",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        package_json = self._substitute(self._read_template("package.json.template"), replacements)
        files.append(ScaffoldFile(
            path="frontend/package.json",
            content=package_json,
            language="json",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        # 5. Database Schema File
        sql_content = db.sql_schema if db else "-- Database Schema\nCREATE TABLE app_health (id INTEGER PRIMARY KEY, status TEXT);"
        files.append(ScaffoldFile(
            path="database/schema.sql",
            content=sql_content,
            language="sql",
            generated_by="DatabaseAgent"
        ))

        # 6. Generated Project Summary
        summary_payload = {
            "project_name": project_name,
            "requirements_generated": req is not None,
            "architecture_generated": arch is not None,
            "database_generated": db is not None,
            "documentation_generated": doc is not None,
            "scaffolded_at": "2026-07-23",
        }
        files.append(ScaffoldFile(
            path="generated/project_summary.json",
            content=json.dumps(summary_payload, indent=2),
            language="json",
            generated_by="ScaffoldAgent (Template Engine)"
        ))

        # Build ASCII Tree View
        tree_lines = [
            f"{project_name}/",
            "├── README.md",
            "├── LICENSE",
            "├── .gitignore",
            "├── .env.example",
            "├── docs/",
            "│   ├── requirements.md",
            "│   ├── architecture.md",
            "│   └── database.md",
            "├── backend/",
            "│   ├── requirements.txt",
            "│   └── app/",
            "│       ├── main.py",
            "│       └── database.py",
            "├── frontend/",
            "│   ├── package.json",
            "│   └── src/",
            "│       └── App.tsx",
            "├── database/",
            "│   └── schema.sql",
            "└── generated/",
            "    └── project_summary.json",
        ]
        tree_view = "\n".join(tree_lines)

        return tree_view, files

"""
Template Loader
---------------
Discovers and reads Jinja2 template files from ``backend/app/templates/``.
Templates are plain‑text files using ``{{ variable }}`` syntax.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class TemplateLoader:
    """Loads raw template strings from the template repository on disk."""

    def __init__(self, templates_dir: Optional[Path] = None) -> None:
        self.templates_dir = templates_dir or TEMPLATES_DIR

    def load(self, template_filename: str) -> str:
        """Return the raw contents of a template file.

        Args:
            template_filename: Filename relative to the templates directory,
                               e.g. ``"fastapi_main.py.template"``.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        filepath = self.templates_dir / template_filename
        if not filepath.is_file():
            raise FileNotFoundError(
                f"Template not found: {filepath}. "
                f"Available templates: {[f.name for f in self.templates_dir.glob('*')]}"
            )
        return filepath.read_text(encoding="utf-8")

    def list_templates(self) -> list[str]:
        """Return a sorted list of all available template filenames."""
        return sorted(f.name for f in self.templates_dir.glob("*") if f.is_file())

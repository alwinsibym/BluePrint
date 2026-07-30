"""
Template Renderer
-----------------
Renders raw template strings by substituting ``{{variable}}`` placeholders
with values from a context dictionary.

Deliberately simple – no external Jinja2 dependency needed for the core
substitution logic (we use str.replace for speed and zero‑deps).
Jinja2‑style blocks ({% if %} etc.) are NOT supported on purpose: generation
logic lives in ``file_generator.py``, not in templates.
"""

from __future__ import annotations


class TemplateRenderer:
    """Replaces ``{{key}}`` tokens in a template string with context values."""

    @staticmethod
    def render(template: str, context: dict) -> str:
        """Render *template* by substituting all ``{{key}}`` tokens.

        Unknown tokens are left in place so they are visible to the developer.

        Args:
            template: Raw template string loaded by ``TemplateLoader``.
            context:  Flat key→value mapping (all values are coerced to ``str``).

        Returns:
            Rendered string with placeholders replaced.
        """
        result = template
        for key, value in context.items():
            result = result.replace("{{" + str(key) + "}}", str(value) if value is not None else "")
        return result

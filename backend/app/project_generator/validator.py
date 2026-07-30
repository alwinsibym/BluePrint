"""
Validator
---------
Post‑generation sanity checks run **after** ``FileGenerator`` has built the file
list and **before** the response is sent to the client.

Checks performed
~~~~~~~~~~~~~~~~
* Required files exist (README.md, backend/app/main.py, frontend/src/App.tsx)
* SQL schema is non‑empty
* No duplicate file paths
* No empty ``content`` for critical files
* ``project_summary.json`` is well‑formed JSON
"""

from __future__ import annotations

import json
from typing import List, Tuple

from app.models.scaffold import ScaffoldFile


REQUIRED_PATHS = {
    "README.md",
    "backend/app/main.py",
    "frontend/src/App.tsx",
    "database/schema.sql",
    "generated/project_summary.json",
}


class GenerationValidator:
    """Validates the output of ``FileGenerator``."""

    def validate(self, files: List[ScaffoldFile]) -> Tuple[bool, List[str]]:
        """Run all checks.

        Args:
            files: List of generated files.

        Returns:
            ``(ok, warnings)`` where *ok* is ``True`` when no critical issues
            were found and *warnings* is a list of human‑readable messages.
        """
        warnings: List[str] = []
        paths = [f.path for f in files]
        path_set = set(paths)

        # 1. Duplicate paths
        if len(paths) != len(path_set):
            seen: set = set()
            for p in paths:
                if p in seen:
                    warnings.append(f"Duplicate file path detected: {p}")
                seen.add(p)

        # 2. Required files present
        for req in REQUIRED_PATHS:
            if req not in path_set:
                warnings.append(f"Required file missing from scaffold: {req}")

        # 3. Empty critical files
        for f in files:
            if f.path in REQUIRED_PATHS and not f.content.strip():
                warnings.append(f"Critical file has empty content: {f.path}")

        # 4. project_summary.json is valid JSON
        for f in files:
            if f.path == "generated/project_summary.json":
                try:
                    json.loads(f.content)
                except json.JSONDecodeError as exc:
                    warnings.append(f"project_summary.json is not valid JSON: {exc}")

        ok = not any("missing" in w or "Duplicate" in w for w in warnings)
        return ok, warnings

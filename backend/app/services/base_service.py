from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any

class BaseService(ABC):
    """Abstract base service providing common utilities for agents.

    Subclasses should implement their own public methods that orchestrate the
    workflow, but can reuse the ``load_prompt`` helper to read a markdown prompt
    from ``backend/app/prompts``.
    """

    @staticmethod
    def load_prompt(prompt_name: str) -> str:
        """Return the raw contents of a prompt file.

        ``prompt_name`` should be the filename without extension, located in
        ``backend/app/prompts``. Raises ``FileNotFoundError`` if the prompt does
        not exist.
        """
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        prompt_path = prompts_dir / f"{prompt_name}.md"
        if not prompt_path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    @abstractmethod
    def description(self) -> str:
        """Return a short description of the service – useful for logging."""
        pass

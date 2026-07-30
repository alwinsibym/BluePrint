"""
Project Context Manager
-----------------------
Thread‑safe singleton that acts as a central in‑memory store for the shared
``ProjectContext``.  Each AI agent reads the current context, appends its own
section, and optionally persists agent‑level metadata (model name, execution
time, token count, status).

Design notes
~~~~~~~~~~~~
* Using a singleton avoids passing the context object through every function call.
* The mutex ensures concurrent FastAPI request handlers cannot corrupt the state.
* ``agent_metadata`` keeps a per‑agent audit trail displayed on the frontend.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AgentMetadata:
    """Lightweight dataclass that records a single agent's execution telemetry."""

    def __init__(
        self,
        agent: str,
        model: str = "qwen2.5-coder",
        status: str = "Completed",
        execution_time: Optional[str] = None,
        tokens: Optional[int] = None,
    ) -> None:
        self.agent = agent
        self.model = model
        self.status = status
        self.execution_time = execution_time or "N/A"
        self.tokens = tokens or 0
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "model": self.model,
            "status": self.status,
            "execution_time": self.execution_time,
            "tokens": self.tokens,
            "timestamp": self.timestamp,
        }


class ProjectContextManager:
    """Thread‑safe singleton managing the shared project context.

    The context is a mutable ``dict`` where each agent stores its output under a
    top‑level key matching the agent domain (e.g. ``"requirements"``).

    Usage::

        ctx = ProjectContextManager()
        ctx.update_section("requirements", req_response.model_dump())
        ctx.record_metadata(AgentMetadata("RequirementsAgent", tokens=1248, execution_time="2.4s"))
    """

    _instance: Optional["ProjectContextManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ProjectContextManager":
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._context: Dict[str, Any] = {}
                inst._metadata: List[Dict[str, Any]] = []
                inst._inner_lock = threading.Lock()
                cls._instance = inst
        return cls._instance

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def get_context(self) -> Dict[str, Any]:
        """Return a shallow copy of the full project context."""
        with self._inner_lock:
            return dict(self._context)

    def update_section(self, section: str, data: Any) -> None:
        """Insert or replace a top‑level ``section`` in the context.

        Args:
            section: Domain key, e.g. ``"requirements"``, ``"architecture"``.
            data:    JSON‑serialisable value (typically a ``dict`` or ``list``).
        """
        with self._inner_lock:
            self._context[section] = data

    def get_section(self, section: str, default: Any = None) -> Any:
        """Retrieve a specific section.  Returns ``default`` when missing."""
        with self._inner_lock:
            return self._context.get(section, default)

    def clear(self) -> None:
        """Reset everything – useful for testing or starting a new project."""
        with self._inner_lock:
            self._context.clear()
            self._metadata.clear()

    # ------------------------------------------------------------------
    # Agent metadata helpers
    # ------------------------------------------------------------------

    def record_metadata(self, meta: AgentMetadata) -> None:
        """Append an agent's execution record to the audit trail."""
        with self._inner_lock:
            self._metadata.append(meta.to_dict())

    def get_metadata(self) -> List[Dict[str, Any]]:
        """Return a copy of all recorded agent metadata entries."""
        with self._inner_lock:
            return list(self._metadata)

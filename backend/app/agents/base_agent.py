from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """Abstract base class for all agents.

    Concrete agents implement :meth:`handle` which receives the primary input
    (e.g., a project idea) and returns a Python object – typically a Pydantic
    model representing the response.
    """

    @abstractmethod
    async def handle(self, *args: Any, **kwargs: Any) -> Any:
        """Process the request and return the result.

        Sub‑classes should be asynchronous to integrate nicely with FastAPI.
        """
        pass

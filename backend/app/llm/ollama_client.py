import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaError(Exception):
    pass

async def generate(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text.

    Reads configuration from ``settings``:
    - OLLAMA_HOST (e.g. http://127.0.0.1:11434)
    - OLLAMA_MODEL (e.g. qwen2.5-coder or qwen2:3.8b)
    - OLLAMA_TEMPERATURE
    - OLLAMA_TIMEOUT
    - OLLAMA_MAX_TOKENS
    """
    url = f"{settings.OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": settings.OLLAMA_TEMPERATURE,
            "num_predict": settings.OLLAMA_MAX_TOKENS,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if "response" not in data:
                raise OllamaError("Invalid response format from Ollama")
            return data["response"].strip()
    except httpx.RequestError as exc:
        raise OllamaError(f"Could not connect to Ollama at {settings.OLLAMA_HOST}: {exc}")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise OllamaError(
                f"Model '{settings.OLLAMA_MODEL}' not found on Ollama server. "
                f"Run 'ollama pull {settings.OLLAMA_MODEL}' in your terminal."
            )
        raise OllamaError(f"Ollama request failed (HTTP {exc.response.status_code}): {exc}")

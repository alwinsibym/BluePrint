import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaError(Exception):
    pass

async def generate(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text.

    Reads configuration from ``settings``:
    - OLLAMA_HOST  (e.g. http://127.0.0.1:11434)
    - OLLAMA_MODEL (e.g. qwen3:8b)
    - OLLAMA_TEMPERATURE
    - OLLAMA_TIMEOUT
    - OLLAMA_MAX_TOKENS
    - OLLAMA_THINK  (False = disable qwen3 thinking, much faster)
    """
    url = f"{settings.OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "think": settings.OLLAMA_THINK,          # disable extended thinking for speed
        "options": {
            "temperature": settings.OLLAMA_TEMPERATURE,
            "num_predict": settings.OLLAMA_MAX_TOKENS,
        },
    }
    logger.info(
        "Ollama request → model=%s think=%s timeout=%ss",
        settings.OLLAMA_MODEL, settings.OLLAMA_THINK, settings.OLLAMA_TIMEOUT,
    )
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if "response" not in data:
                raise OllamaError("Invalid response format from Ollama — 'response' key missing")
            text = data["response"].strip()
            logger.info("Ollama responded with %d chars", len(text))
            return text
    except httpx.ReadTimeout:
        raise OllamaError(
            f"Ollama timed out after {settings.OLLAMA_TIMEOUT}s. "
            "The model is still loading or the prompt is too large. "
            "Try increasing OLLAMA_TIMEOUT or using a smaller model."
        )
    except httpx.RequestError as exc:
        raise OllamaError(f"Could not connect to Ollama at {settings.OLLAMA_HOST}: {exc}")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise OllamaError(
                f"Model '{settings.OLLAMA_MODEL}' not found. "
                f"Run: ollama pull {settings.OLLAMA_MODEL}"
            )
        raise OllamaError(f"Ollama HTTP error {exc.response.status_code}: {exc}")


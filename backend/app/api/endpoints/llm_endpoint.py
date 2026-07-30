from fastapi import APIRouter, HTTPException

from app.llm.ollama_client import generate, OllamaError

router = APIRouter()

@router.post("/test-llm")
async def handle_test_llm(payload: dict):
    """Receive a JSON payload with a 'prompt' field, forward it to Ollama, and return the response.
    Returns JSON: {"response": "..."}.
    Errors are converted to HTTPException with clear detail messages.
    """
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' field")
    try:
        response = await generate(prompt)
        return {"response": response}
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

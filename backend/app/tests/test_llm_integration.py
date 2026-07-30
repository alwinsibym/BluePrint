import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.main import app

@pytest.mark.asyncio
async def test_llm_endpoint_success(monkeypatch):
    # Mock Ollama client to avoid real HTTP call
    async def mock_generate(prompt: str) -> str:
        return f"Mock response to: {prompt}"
    monkeypatch.setattr("app.api.endpoints.llm_endpoint.generate", mock_generate)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.post("/test/test-llm", json={"prompt": "Hello"})
        assert response.status_code == 200
        json_data = response.json()
        assert "response" in json_data
        assert json_data["response"] == "Mock response to: Hello"

@pytest.mark.asyncio
async def test_llm_endpoint_missing_prompt(monkeypatch):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.post("/test/test-llm", json={})
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing 'prompt' field"

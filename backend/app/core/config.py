# backend/app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = Field(default="Blueprint", description="Application name")
    
    # Ollama settings
    OLLAMA_HOST: str = Field(default="http://127.0.0.1:11434", description="Ollama host URL")
    OLLAMA_MODEL: str = Field(default="qwen3:8b", description="Default Ollama model name")
    OLLAMA_TEMPERATURE: float = Field(default=0.3, description="Generation temperature — lower = more deterministic JSON")
    OLLAMA_TIMEOUT: int = Field(default=600, description="Request timeout in seconds — 10 min for large prompts")
    OLLAMA_MAX_TOKENS: int = Field(default=3000, description="Maximum tokens per response")

    # Disable qwen3 'thinking' mode — it adds massive latency with no benefit for structured JSON
    OLLAMA_THINK: bool = Field(default=False, description="Set True to enable qwen3 extended thinking (very slow)")
    
    # Agent retries — keep at 1 to avoid 3x timeout stacking on failure
    REQUIREMENTS_AGENT_RETRY_COUNT: int = Field(default=1, description="Number of LLM response parse retries for RequirementsAgent")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

settings = Settings()

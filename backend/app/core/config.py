# backend/app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = Field(default="Blueprint", description="Application name")
    
    # Ollama settings
    OLLAMA_HOST: str = Field(default="http://127.0.0.1:11434", description="Ollama host URL")
    OLLAMA_MODEL: str = Field(default="qwen3:8b", description="Default Ollama model name")
    OLLAMA_TEMPERATURE: float = Field(default=0.7, description="Generation temperature")
    OLLAMA_TIMEOUT: int = Field(default=120, description="Request timeout seconds")
    OLLAMA_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens per response")
    
    # Agent retries
    REQUIREMENTS_AGENT_RETRY_COUNT: int = Field(default=3, description="Number of LLM response parse retries for RequirementsAgent")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    DATABASE_URL: str

    LLM_PROVIDER: str = "openrouter"

    OPENROUTER_API_KEY: Optional[str] = None

    HUGGINGFACE_API_KEY: Optional[str] = None
    HF_MODEL: Optional[str] = None

    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None

    OLLAMA_MODEL: Optional[str] = "mistral"
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
import requests

from app.core.config import settings

from app.llm.base import BaseLLM


class OllamaProvider(BaseLLM):

    def __init__(self):
        if not all([settings.OLLAMA_MODEL, settings.OLLAMA_BASE_URL]):
            raise ValueError("Ollama requires OLLAMA_MODEL and OLLAMA_BASE_URL to be set in .env")

    def generate(self, messages):

        prompt = messages[-1]["content"]

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return {
            "content": data["response"],
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
from openai import OpenAI

from app.core.config import settings

from app.llm.base import BaseLLM


class OpenRouterProvider(BaseLLM):

    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter requires OPENROUTER_API_KEY to be set in .env")

        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

    def generate(self, messages):
        response = self.client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages
        )

        return {
            "content": response.choices[0].message.content,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
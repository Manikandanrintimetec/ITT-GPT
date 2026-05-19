from app.llm.providers.openrouter_provider import OpenRouterProvider
from app.llm.providers.azure_provider import AzureProvider
from app.llm.providers.huggingface_provider import HuggingFaceProvider
from app.llm.providers.ollama_provider import OllamaProvider


class LLMFactory:

    @staticmethod
    def get_llm(provider: str):

        provider = provider.lower()

        if provider == "openrouter":
            return OpenRouterProvider()

        if provider == "openai":
            return AzureProvider()

        if provider == "huggingface":
            return HuggingFaceProvider()
        
        if provider == "ollama":
            return OllamaProvider()

        raise ValueError("Invalid provider")
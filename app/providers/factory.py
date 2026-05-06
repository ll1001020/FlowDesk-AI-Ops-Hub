from app.config import Settings
from .base import LLMProvider
from .mock import MockProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider


def build_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower().strip()
    if provider == "mock":
        return MockProvider()
    if provider == "openai_compatible":
        return OpenAICompatibleProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )
    if provider == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url, model=settings.llm_model)
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")

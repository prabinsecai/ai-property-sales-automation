"""Provider-neutral text generation with an offline deterministic provider."""
from abc import ABC, abstractmethod
from .config import get_settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, context: str = "") -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, *, context: str = "") -> str:
        if context:
            return f"Based on the available property information: {context}"
        return "I can help with property availability, pricing, and inspections."


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate(self, prompt: str, *, context: str = "") -> str:
        result = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": context}, {"role": "user", "content": prompt}],
        )
        return result.choices[0].message.content or ""


class AnthropicCompatibleProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise RuntimeError("anthropic package is required for LLM_MODE=anthropic") from exc
        self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate(self, prompt: str, *, context: str = "") -> str:
        result = await self.client.messages.create(
            model=self.model, max_tokens=1000, system=context,
            messages=[{"role": "user", "content": prompt}],
        )
        return result.content[0].text if result.content else ""


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    mode = settings.llm_mode.lower()
    if mode in ("mock", "deterministic"):
        return MockLLMProvider()
    if mode in ("openai", "openai-compatible"):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_MODE=openai")
        return OpenAICompatibleProvider(settings.openai_api_key, settings.llm_model,
                                        settings.openai_base_url)
    if mode in ("anthropic", "anthropic-compatible"):
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required when LLM_MODE=anthropic")
        return AnthropicCompatibleProvider(settings.anthropic_api_key, settings.anthropic_model,
                                           settings.anthropic_base_url)
    raise RuntimeError(f"Unsupported LLM_MODE: {settings.llm_mode}")

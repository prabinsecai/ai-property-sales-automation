import hashlib
import math
from collections.abc import Sequence


class EmbeddingProvider:
    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError


class DeterministicEmbedding(EmbeddingProvider):
    """Stable local vectors for tests and offline development."""
    dimensions = 64

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            raw = hashlib.sha256(text.lower().encode()).digest()
            values = [((raw[i % len(raw)] / 255.0) * 2) - 1 for i in range(self.dimensions)]
            norm = math.sqrt(sum(v * v for v in values)) or 1
            vectors.append([v / norm for v in values])
        return vectors


class OpenAIEmbedding(EmbeddingProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def get_embedding_provider() -> EmbeddingProvider:
    from .config import get_settings
    settings = get_settings()
    if settings.embedding_mode.lower() == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_MODE=openai")
        return OpenAIEmbedding(settings.openai_api_key, settings.openai_embedding_model,
                               settings.openai_base_url)
    return DeterministicEmbedding()

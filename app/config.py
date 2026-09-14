from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./properties.db"
    embedding_mode: str = "deterministic"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    chroma_path: str = "./.chroma"
    top_k: int = 10
    llm_mode: str = "mock"
    llm_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_base_url: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    frontend_url: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

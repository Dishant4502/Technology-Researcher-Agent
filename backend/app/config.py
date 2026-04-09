from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_REPO_DIR = BASE_DIR / "knowledge_repo"


class Settings(BaseSettings):
    app_name: str = "Technology Autonomous Researcher"
    api_prefix: str = "/api"
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4.1-mini")
    openai_base_url: str | None = Field(default="")
    tavily_api_key: str | None = Field(default=None)
    allowed_origins: str = Field(default="http://localhost:5173")
    research_max_sources: int = Field(default=6)
    knowledge_retention_limit: int = Field(default=8)
    knowledge_retention_limit: int = 10

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    @property
    def llm_api_key(self) -> str:
        return self.groq_api_key or self.openai_api_key

    @property
    def llm_model(self) -> str:
        return self.groq_model if self.groq_api_key else self.openai_model

    @property
    def llm_base_url(self) -> str | None:
        if self.groq_api_key:
            return self.groq_base_url
        return self.openai_base_url or None

    @property
    def llm_provider(self) -> str:
        return "groq" if self.groq_api_key else "openai"


@lru_cache
def get_settings() -> Settings:
    KNOWLEDGE_REPO_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()

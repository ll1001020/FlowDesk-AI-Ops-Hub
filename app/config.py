from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FlowDesk AI Ops Hub"
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="flowdesk-mock", alias="LLM_MODEL")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    database_url: str = Field(default="sqlite:///./flowdesk.db", alias="DATABASE_URL")
    knowledge_dir: str = Field(default="./data/knowledge", alias="KNOWLEDGE_DIR")

    @property
    def knowledge_path(self) -> Path:
        return Path(self.knowledge_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()

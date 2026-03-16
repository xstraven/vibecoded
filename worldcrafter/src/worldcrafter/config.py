from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_NOTES_DIR = Path("/Users/david/Obsidian/Projects/Worldcrafter")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    openrouter_default_model: str = Field(
        default="deepseek/deepseek-v3.2",
        alias="OPENROUTER_DEFAULT_MODEL",
    )
    worldcrafter_notes_dir: Path = Field(
        default=DEFAULT_NOTES_DIR,
        alias="WORLDCRAFTER_NOTES_DIR",
    )

    @property
    def example_game_dir(self) -> Path:
        return self.worldcrafter_notes_dir / "example_game"

    @property
    def worlds_dir(self) -> Path:
        return self.example_game_dir / "worlds"


@lru_cache
def get_settings() -> Settings:
    return Settings()

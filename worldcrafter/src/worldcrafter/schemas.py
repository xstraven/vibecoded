from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GenerateWorldRequest(BaseModel):
    concept: str = Field(min_length=3)
    genre: str | None = None
    premise: str | None = None


class WorldBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    background_story: str = Field(min_length=1)
    opening_setup: str = Field(min_length=1)
    first_action: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    hidden_instructions: str = Field(min_length=1)
    author_notes: str = Field(min_length=1)


class StoredWorldRecord(BaseModel):
    world_id: str
    slug: str
    file_path: str
    blueprint: WorldBlueprint


class FrontmatterRecord(BaseModel):
    id: str
    slug: str
    title: str
    summary: str
    objective: str
    status: Literal["draft"] = "draft"
    visibility: Literal["private"] = "private"
    model: str
    created_at: datetime
    source_concept: str

    def as_serializable_dict(self) -> dict[str, str]:
        payload = self.model_dump()
        payload["created_at"] = self.created_at.astimezone(timezone.utc).isoformat()
        return payload

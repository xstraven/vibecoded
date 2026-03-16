from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException

from worldcrafter.config import Settings, get_settings
from worldcrafter.openrouter import OpenRouterError
from worldcrafter.schemas import GenerateWorldRequest, StoredWorldRecord
from worldcrafter.service import WorldCreationService

app = FastAPI(title="Worldcrafter")


@lru_cache
def get_world_creation_service() -> WorldCreationService:
    settings = get_settings()
    return WorldCreationService(settings=settings)


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ok", "model": settings.openrouter_default_model}


@app.post("/api/worlds/generate", response_model=StoredWorldRecord)
async def generate_world(
    request: GenerateWorldRequest,
    service: WorldCreationService = Depends(get_world_creation_service),
) -> StoredWorldRecord:
    try:
        return await service.generate_world(request)
    except OpenRouterError as exc:
        raise HTTPException(
            status_code=502,
            detail="OpenRouter failed to return a valid structured world blueprint.",
        ) from exc

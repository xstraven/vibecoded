from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from worldcrafter.config import Settings
from worldcrafter.schemas import GenerateWorldRequest, WorldBlueprint


class OpenRouterError(RuntimeError):
    """Raised when the OpenRouter call fails or returns invalid data."""


class OpenRouterWorldGenerator:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._client = client

    async def generate_blueprint(self, request: GenerateWorldRequest) -> WorldBlueprint:
        payload = {
            "model": self.settings.openrouter_default_model,
            "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": build_user_prompt(request)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "world_blueprint",
                    "strict": True,
                    "schema": WorldBlueprint.model_json_schema(),
                },
            },
        }

        client = self._client or httpx.AsyncClient(
            base_url=self.settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

        close_client = self._client is None
        try:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            content = extract_content(data)
            return WorldBlueprint.model_validate_json(content)
        except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise OpenRouterError("Failed to generate a valid structured world blueprint.") from exc
        finally:
            if close_client:
                await client.aclose()


def build_system_prompt() -> str:
    return (
        "You generate concise but flavorful world blueprints for an RPG text sandbox. "
        "Return only structured JSON that matches the requested schema. "
        "Make the world playable, coherent, and easy to expand later. "
        "Write clear hidden instructions that guide tone, pacing, and progression."
    )


def build_user_prompt(request: GenerateWorldRequest) -> str:
    parts = [f"Concept: {request.concept}"]
    if request.genre:
        parts.append(f"Genre: {request.genre}")
    if request.premise:
        parts.append(f"Premise: {request.premise}")
    parts.append(
        "Create a first-draft world with a strong hook, a clear objective, and room for player choice."
    )
    return "\n".join(parts)


def extract_content(payload: dict[str, Any]) -> str:
    content = payload["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        fragments = []
        for item in content:
            text = item.get("text")
            if text:
                fragments.append(text)
        if fragments:
            return "".join(fragments)
    raise KeyError("Missing structured content in OpenRouter response.")

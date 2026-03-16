from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from worldcrafter.config import Settings
from worldcrafter.main import app, get_settings, get_world_creation_service
from worldcrafter.openrouter import OpenRouterError
from worldcrafter.schemas import GenerateWorldRequest, StoredWorldRecord, WorldBlueprint


class FakeWorldCreationService:
    def __init__(self, *, result: StoredWorldRecord | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error

    async def generate_world(self, request: GenerateWorldRequest) -> StoredWorldRecord:
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


def build_settings(tmp_path: Path) -> Settings:
    return Settings(
        OPENROUTER_API_KEY="test-key",
        OPENROUTER_BASE_URL="https://openrouter.ai/api/v1",
        OPENROUTER_DEFAULT_MODEL="deepseek/deepseek-v3.2",
        WORLDCRAFTER_NOTES_DIR=tmp_path,
    )


def build_record(tmp_path: Path) -> StoredWorldRecord:
    file_path = tmp_path / "example_game" / "worlds" / "clockwork-harbor.md"
    return StoredWorldRecord(
        world_id="world-123",
        slug="clockwork-harbor",
        file_path=str(file_path),
        blueprint=WorldBlueprint(
            title="Clockwork Harbor",
            summary="A city of tides and machines.",
            background_story="The harbor runs on ancient engines.",
            opening_setup="You arrive during a blackout festival.",
            first_action="Step onto the lantern-lit docks and choose who to trust.",
            objective="Discover who is sabotaging the engines.",
            hidden_instructions="Keep the tone adventurous and tense.",
            author_notes="Seed rival factions early.",
        ),
    )


def test_health_returns_ok(tmp_path: Path) -> None:
    app.dependency_overrides[get_settings] = lambda: build_settings(tmp_path)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "deepseek/deepseek-v3.2"}
    app.dependency_overrides.clear()


def test_generate_world_returns_structured_record(tmp_path: Path) -> None:
    app.dependency_overrides[get_settings] = lambda: build_settings(tmp_path)
    app.dependency_overrides[get_world_creation_service] = lambda: FakeWorldCreationService(
        result=build_record(tmp_path)
    )
    client = TestClient(app)

    response = client.post(
        "/api/worlds/generate",
        json={"concept": "A mystery in a mechanical port city"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "clockwork-harbor"
    assert data["blueprint"]["title"] == "Clockwork Harbor"
    app.dependency_overrides.clear()


def test_generate_world_returns_502_on_generator_failure(tmp_path: Path) -> None:
    app.dependency_overrides[get_settings] = lambda: build_settings(tmp_path)
    app.dependency_overrides[get_world_creation_service] = lambda: FakeWorldCreationService(
        error=OpenRouterError("bad response")
    )
    client = TestClient(app)

    response = client.post(
        "/api/worlds/generate",
        json={"concept": "A mystery in a mechanical port city"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenRouter failed to return a valid structured world blueprint."
    app.dependency_overrides.clear()

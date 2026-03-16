from __future__ import annotations

from pathlib import Path

from worldcrafter.schemas import WorldBlueprint
from worldcrafter.storage import MarkdownWorldStorage, slugify


def make_blueprint(title: str = "Clockwork Harbor") -> WorldBlueprint:
    return WorldBlueprint(
        title=title,
        summary="A city of tides and machines.",
        background_story="The harbor runs on ancient engines.",
        opening_setup="You arrive during a blackout festival.",
        first_action="Step onto the lantern-lit docks and choose who to trust.",
        objective="Discover who is sabotaging the engines.",
        hidden_instructions="Keep the tone adventurous and tense.",
        author_notes="Seed rival factions early.",
    )


def test_slugify_falls_back_for_non_alphanumeric() -> None:
    assert slugify("!!!") == "world"


def test_save_world_creates_markdown_file(tmp_path: Path) -> None:
    storage = MarkdownWorldStorage(tmp_path / "worlds")
    record = storage.save_world(
        blueprint=make_blueprint(),
        source_concept="A mystery in a mechanical port city",
        model_name="deepseek/deepseek-v3.2",
    )

    output_path = Path(record.file_path)
    content = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert record.slug == "clockwork-harbor"
    assert "status: draft" in content
    assert "visibility: private" in content
    assert "# Clockwork Harbor" in content
    assert "## Hidden Instructions" in content
    assert "source_concept: A mystery in a mechanical port city" in content


def test_save_world_adds_numeric_suffix_for_collisions(tmp_path: Path) -> None:
    storage = MarkdownWorldStorage(tmp_path / "worlds")

    first = storage.save_world(
        blueprint=make_blueprint(),
        source_concept="first",
        model_name="model-a",
    )
    second = storage.save_world(
        blueprint=make_blueprint(),
        source_concept="second",
        model_name="model-a",
    )

    assert first.slug == "clockwork-harbor"
    assert second.slug == "clockwork-harbor-2"

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml

from worldcrafter.schemas import FrontmatterRecord, StoredWorldRecord, WorldBlueprint


class MarkdownWorldStorage:
    def __init__(self, worlds_dir: Path) -> None:
        self.worlds_dir = worlds_dir

    def save_world(
        self,
        *,
        blueprint: WorldBlueprint,
        source_concept: str,
        model_name: str,
    ) -> StoredWorldRecord:
        self.worlds_dir.mkdir(parents=True, exist_ok=True)

        world_id = str(uuid4())
        slug = self._build_unique_slug(blueprint.title)
        file_path = self.worlds_dir / f"{slug}.md"
        frontmatter = FrontmatterRecord(
            id=world_id,
            slug=slug,
            title=blueprint.title,
            summary=blueprint.summary,
            objective=blueprint.objective,
            model=model_name,
            created_at=datetime.now(timezone.utc),
            source_concept=source_concept,
        )

        file_path.write_text(
            self._render_markdown(frontmatter=frontmatter, blueprint=blueprint),
            encoding="utf-8",
        )

        return StoredWorldRecord(
            world_id=world_id,
            slug=slug,
            file_path=str(file_path),
            blueprint=blueprint,
        )

    def _build_unique_slug(self, title: str) -> str:
        base_slug = slugify(title)
        candidate = base_slug
        suffix = 2

        while (self.worlds_dir / f"{candidate}.md").exists():
            candidate = f"{base_slug}-{suffix}"
            suffix += 1

        return candidate

    @staticmethod
    def _render_markdown(
        *,
        frontmatter: FrontmatterRecord,
        blueprint: WorldBlueprint,
    ) -> str:
        yaml_blob = yaml.safe_dump(
            frontmatter.as_serializable_dict(),
            sort_keys=False,
            allow_unicode=False,
        ).strip()
        sections = [
            f"# {blueprint.title}",
            "## Background Story",
            blueprint.background_story,
            "## Opening Setup",
            blueprint.opening_setup,
            "## First Action",
            blueprint.first_action,
            "## Hidden Instructions",
            blueprint.hidden_instructions,
            "## Author Notes",
            blueprint.author_notes,
        ]
        body = "\n\n".join(sections).strip() + "\n"
        return f"---\n{yaml_blob}\n---\n\n{body}"


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "world"

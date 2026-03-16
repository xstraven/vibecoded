from __future__ import annotations

from worldcrafter.config import Settings
from worldcrafter.openrouter import OpenRouterWorldGenerator
from worldcrafter.schemas import GenerateWorldRequest, StoredWorldRecord
from worldcrafter.storage import MarkdownWorldStorage


class WorldCreationService:
    def __init__(
        self,
        *,
        settings: Settings,
        generator: OpenRouterWorldGenerator | None = None,
        storage: MarkdownWorldStorage | None = None,
    ) -> None:
        self.settings = settings
        self.generator = generator or OpenRouterWorldGenerator(settings)
        self.storage = storage or MarkdownWorldStorage(settings.worlds_dir)

    async def generate_world(self, request: GenerateWorldRequest) -> StoredWorldRecord:
        blueprint = await self.generator.generate_blueprint(request)
        return self.storage.save_world(
            blueprint=blueprint,
            source_concept=request.concept,
            model_name=self.settings.openrouter_default_model,
        )

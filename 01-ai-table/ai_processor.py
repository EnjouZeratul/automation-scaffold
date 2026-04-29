from __future__ import annotations

from shared.config.settings import Settings
from shared.utils.bailian import BailianClient


class AIProcessor:
    def __init__(self, settings: Settings):
        self.client = BailianClient(
            api_key=settings.bailian.api_key,
            base_url=settings.bailian.base_url,
            model=settings.bailian.model,
        )

    async def process_field(
        self, text: str, task: str = "classification", categories: list[str] | None = None
    ) -> str:
        if task == "classification" and categories:
            return await self.client.classify_text(text, categories)
        elif task == "sentiment":
            return await self.client.sentiment_analysis(text)
        raise ValueError(f"不支持的任务: {task}")

    async def batch_process(
        self, texts: list[str], task: str = "classification", categories: list[str] | None = None
    ) -> list[str]:
        import asyncio
        coros = [self.process_field(t, task, categories) for t in texts]
        return await asyncio.gather(*coros)

    async def close(self):
        await self.client.close()

from __future__ import annotations

from typing import Any

from shared.utils.bailian import BailianClient


class BailianAnalyzeTool:
    def __init__(self, api_key: str, base_url: str, model: str = "qwen-plus"):
        self.client = BailianClient(api_key, base_url, model)

    async def execute(self, task: str, text: str, **kwargs) -> str:
        if task == "classification":
            cats = kwargs.get("categories", ["正面", "中性", "负面"])
            return await self.client.classify_text(text, cats)
        elif task == "sentiment":
            return await self.client.sentiment_analysis(text)
        elif task == "general":
            return await self.client.chat([{"role": "user", "content": text}])
        raise ValueError(f"未知任务: {task}")

    async def close(self):
        await self.client.close()

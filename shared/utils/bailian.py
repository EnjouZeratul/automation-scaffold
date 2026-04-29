from __future__ import annotations

import asyncio
from typing import Any

import httpx


class BailianClient:
    """百炼 API 客户端（OpenAI 兼容模式）"""

    def __init__(self, api_key: str, base_url: str, model: str = "qwen-plus"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        if "response_format" in kwargs:
            body["response_format"] = kwargs["response_format"]

        resp = await self._client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def classify_text(self, text: str, categories: list[str]) -> str:
        """文本分类"""
        msg = (
            f"请对以下文本进行分类，只能从以下类别中选一个：{', '.join(categories)}\n\n"
            f"文本：{text}\n\n"
            f"只输出类别名称，不要其他内容。"
        )
        result = await self.chat([{"role": "user", "content": msg}])
        return result.strip()

    async def sentiment_analysis(self, text: str) -> str:
        """情感分析：正面/中性/负面"""
        msg = (
            f"请分析以下文本的情感倾向，只能回复：正面、中性 或 负面。\n\n"
            f"文本：{text}\n\n"
            f"只输出情感倾向，不要其他内容。"
        )
        result = await self.chat([{"role": "user", "content": msg}])
        return result.strip()

    async def close(self):
        await self._client.aclose()

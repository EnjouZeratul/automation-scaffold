from __future__ import annotations

import os
from typing import Any

import httpx


class WebSearchTool:
    """通用联网搜索工具（预留搜索引擎 API 接入点）"""

    def __init__(self, search_api_url: str = "", api_key: str = ""):
        self.search_api_url = search_api_url
        self.api_key = api_key

    async def execute(self, query: str, num_results: int = 5) -> dict[str, Any]:
        if self.search_api_url:
            return await self._search_via_api(query, num_results)
        return await self._search_fallback(query)

    async def _search_via_api(self, query: str, n: int) -> dict:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                self.search_api_url, params={"q": query, "num": n}, headers=headers
            )
            resp.raise_for_status()
            return resp.json()

    async def _search_fallback(self, query: str) -> dict:
        """降级：使用百炼 LLM 做知识问答"""
        from shared.utils.bailian import BailianClient
        client = BailianClient(
            api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        )
        result = await client.chat(
            [
                {
                    "role": "system",
                    "content": "你是一个搜索助手，根据用户问题提供简洁准确的答案。",
                },
                {"role": "user", "content": query},
            ],
            max_tokens=1024,
        )
        return {"results": [{"snippet": result}]}

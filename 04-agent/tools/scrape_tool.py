from __future__ import annotations

from typing import Any

import httpx


class ScrapeDataTool:
    """触发数据抓取（预留接口）"""

    def __init__(self, scraper_url: str, api_key: str = ""):
        self.scraper_url = scraper_url
        self.api_key = api_key

    async def execute(self, source_type: str, config: dict[str, Any]) -> dict:
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            resp = await client.post(
                f"{self.scraper_url}/scrape/{source_type}", json=config
            )
            resp.raise_for_status()
            return resp.json()

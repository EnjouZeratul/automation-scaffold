from __future__ import annotations

from typing import Any

import httpx


class RPATriggerTool:
    """触发 RPA 任务（预留接口）"""

    def __init__(self, rpa_mcp_url: str = ""):
        self.rpa_mcp_url = rpa_mcp_url

    async def execute(self, script_name: str, params: dict[str, Any]) -> dict:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.rpa_mcp_url}/rpa/trigger",
                json={"script": script_name, "params": params},
            )
            resp.raise_for_status()
            return resp.json()

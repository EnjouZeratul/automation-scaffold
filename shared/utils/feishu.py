from __future__ import annotations

import time
from typing import Any

import httpx


class FeishuClient:
    BASE_URL = "https://open.feishu.cn"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token: str = ""
        self._token_expire: float = 0

    async def _get_tenant_token(self) -> str:
        if time.time() < self._token_expire - 300:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["tenant_access_token"]
            self._token_expire = time.time() + data.get("expire", 7200)
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_tenant_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def create_spreadsheet(
        self, folder_token: str, title: str
    ) -> dict[str, Any]:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/open-apis/sheets/v2/spreadsheets",
                headers=headers,
                json={"title": title, "folder_token": folder_token},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_values(
        self, spreadsheet_token: str, sheet_id: str, range: str = "A1:Z1000"
    ) -> dict[str, Any]:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}",
                headers=headers,
                params={"range": range},
            )
            resp.raise_for_status()
            return resp.json()

    async def update_values(
        self, spreadsheet_token: str, sheet_id: str, range_str: str, values: list[list[Any]]
    ) -> dict[str, Any]:
        """更新单元格值。values 是行列二维数组，如 [["A1","B1"],["A2","B2"]]"""
        headers = await self._headers()
        full_range = f"{sheet_id}!{range_str}"
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.BASE_URL}/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values",
                headers=headers,
                json={
                    "valueRange": {
                        "range": full_range,
                        "values": values,
                    }
                },
            )
            resp.raise_for_status()
            return resp.json()

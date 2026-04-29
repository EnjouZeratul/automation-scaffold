from __future__ import annotations

from typing import Any

import httpx
from shared.config.settings import Settings
from shared.utils.dingtalk import DingTalkClient
from shared.utils.feishu import FeishuClient


class TableOperations:
    def __init__(self, settings: Settings):
        self.platform = settings.spreadsheet_platform
        if self.platform == "dingtalk":
            self.client = DingTalkClient(
                settings.dingtalk.app_key, settings.dingtalk.app_secret
            )
        else:
            self.client = FeishuClient(
                settings.feishu.app_id, settings.feishu.app_secret
            )

    async def create_table(self, title: str, **kwargs) -> dict[str, Any]:
        if self.platform == "dingtalk":
            return await self.client.create_spreadsheet(title, kwargs.get("folder_id", ""))
        return await self.client.create_spreadsheet(kwargs.get("folder_token", ""), title)

    async def append_rows(
        self, spreadsheet_token: str, sheet_id: str, rows: list[list[Any]]
    ) -> dict:
        """追加行数据"""
        if self.platform == "dingtalk":
            dt_rows = [[{"v": cell} for cell in row] for row in rows]
            return await self.client.batch_update_values(
                spreadsheet_token, f"{sheet_id}!A1", dt_rows
            )
        return await self.client.update_values(
            spreadsheet_token, sheet_id, "A1", rows
        )

    async def get_rows(self, spreadsheet_token: str, sheet_id: str, range: str = "") -> list:
        """读取行数据"""
        if self.platform == "dingtalk":
            r = range or f"{sheet_id}!A1:Z1000"
            data = await self.client.get_values(spreadsheet_token, r)
            return data.get("rows", [])
        r = range or "A1:Z1000"
        data = await self.client.get_values(spreadsheet_token, sheet_id, r)
        value_range = data.get("data", {}).get("valueRange", {})
        return value_range.get("values", [])

    async def update_rows(
        self, spreadsheet_token: str, sheet_id: str, start_coord: str, rows: list[list[Any]]
    ) -> dict:
        if self.platform == "dingtalk":
            dt_rows = [[{"v": cell} for cell in row] for row in rows]
            return await self.client.batch_update_values(
                spreadsheet_token, f"{sheet_id}!{start_coord}", dt_rows
            )
        return await self.client.update_values(
            spreadsheet_token, sheet_id, start_coord, rows
        )

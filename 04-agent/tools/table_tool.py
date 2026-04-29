from __future__ import annotations

import sys
from pathlib import Path

from shared.config.settings import Settings

# 01-ai-table 在同一 workspace 中
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "01-ai-table"))

from table_ops import TableOperations


class TableQueryTool:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ops = TableOperations(settings)

    async def execute(
        self, spreadsheet_token: str, sheet_id: str, query: str = ""
    ) -> list:
        rows = await self.ops.get_rows(spreadsheet_token, sheet_id)
        return [list(r) if hasattr(r, "__iter__") and not isinstance(r, (str, dict)) else [r] for r in rows]

    async def push(
        self, spreadsheet_token: str, sheet_id: str, rows: list[list]
    ) -> dict:
        return await self.ops.append_rows(spreadsheet_token, sheet_id, rows)

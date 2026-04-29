from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# 01-ai-table 在同一 workspace 中
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "01-ai-table"))

from table_ops import TableOperations
from shared.config.settings import Settings

logger = logging.getLogger("scraper.writer")


async def write_to_table(
    df: pd.DataFrame,
    settings: Settings,
    spreadsheet_token: str,
    sheet_id: str,
):
    ops = TableOperations(settings)
    rows = [list(row) for row in df.values]
    header = [str(c) for c in df.columns]
    all_rows = [header] + rows
    await ops.append_rows(spreadsheet_token, sheet_id, all_rows)
    logger.info(f"写入表格: {spreadsheet_token} ({len(df)} 行)")

from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger("scraper.writer")


def write_to_db(
    df: pd.DataFrame, connection_url: str, table: str, if_exists: str = "append"
):
    engine = create_engine(connection_url)
    df.to_sql(table, con=engine, if_exists=if_exists, index=False)
    logger.info(f"写入数据库: {table} ({len(df)} 行)")

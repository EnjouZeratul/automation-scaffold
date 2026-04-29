import re

import pandas as pd

from .base import BaseProcessor


class WebScrapeProcessor(BaseProcessor):
    """清洗网页采集数据"""

    def __init__(self, column_mappings: dict | None = None):
        self.column_mappings = column_mappings or {}

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.drop_duplicates()
        df = df.fillna("")
        df.columns = [self._normalize_col(c) for c in df.columns]
        if self.column_mappings:
            df = df.rename(columns=self.column_mappings)
        return df

    @staticmethod
    def _normalize_col(col: str) -> str:
        col = str(col).strip().lower()
        col = re.sub(r"[\s\-]+", "_", col)
        col = re.sub(r"[^a-z0-9_]", "", col)
        return col

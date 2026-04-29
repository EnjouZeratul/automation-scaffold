import pandas as pd

from .base import BaseProcessor


class ReportExportProcessor(BaseProcessor):
    """解析报表数据"""

    def __init__(self, amount_columns: list[str] | None = None, date_columns: list[str] | None = None):
        self.amount_columns = amount_columns or []
        self.date_columns = date_columns or []

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for col in self.amount_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ""), errors="coerce"
                ).fillna(0)
        for col in self.date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return df

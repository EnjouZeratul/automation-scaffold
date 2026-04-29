from __future__ import annotations

import re

import pandas as pd


class DataNormalizer:
    """统一数据清洗"""

    def normalize(
        self, df: pd.DataFrame,
        date_columns: list[str] | None = None,
        numeric_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        df = df.copy()
        # 列名标准化
        df.columns = [self._normalize_col(c) for c in df.columns]
        # 空值处理
        df = df.replace(["NA", "N/A", "null", "None", ""], pd.NA)
        # 数值列
        for col in (numeric_columns or []):
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ""), errors="coerce"
                )
        # 日期列
        for col in (date_columns or []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return df

    @staticmethod
    def _normalize_col(col: str) -> str:
        col = str(col).strip().lower()
        col = re.sub(r"[\s\-]+", "_", col)
        col = re.sub(r"[^a-z0-9_]", "", col)
        return col

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """输入原始 DataFrame，返回清洗后的 DataFrame"""
        pass

    def load_csv(self, path: str, **kwargs) -> pd.DataFrame:
        return pd.read_csv(path, **kwargs)

    def load_excel(self, path: str, **kwargs) -> pd.DataFrame:
        return pd.read_excel(path, **kwargs)

    def save(self, df: pd.DataFrame, path: str):
        if path.endswith(".csv"):
            df.to_csv(path, index=False, encoding="utf-8-sig")
        elif path.endswith((".xlsx", ".xls")):
            df.to_excel(path, index=False)

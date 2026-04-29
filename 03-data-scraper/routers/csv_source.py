from __future__ import annotations

import logging

import pandas as pd
from fastapi import APIRouter, UploadFile, File

from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.csv")
normalizer = DataNormalizer()


@router.post("")
async def import_csv(file: UploadFile = File(...)):
    logger.info(f"导入 CSV: {file.filename}")
    content = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(content))
    df = normalizer.normalize(df)
    logger.info(f"CSV 清洗完成: {len(df)} 行")
    return {
        "count": len(df),
        "columns": list(df.columns),
        "preview": df.head(10).to_dict(orient="records"),
    }

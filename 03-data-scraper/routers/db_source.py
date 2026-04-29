from __future__ import annotations

import logging
import re

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.db")
normalizer = DataNormalizer()

_DANGEROUS_RE = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|TRUNCATE|ALTER|CREATE)\b", re.I
)


class DbQueryRequest(BaseModel):
    connection_url: str
    query: str
    params: dict[str, str] = {}


@router.post("")
async def query_db(req: DbQueryRequest):
    if _DANGEROUS_RE.search(req.query):
        return {"error": "只支持 SELECT 查询"}
    logger.info(f"执行 DB 查询: {req.query[:80]}")
    engine = create_engine(req.connection_url)
    with engine.connect() as conn:
        result = conn.execute(text(req.query), req.params)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    df = normalizer.normalize(df)
    return {
        "count": len(df),
        "columns": list(df.columns),
        "preview": df.head(10).to_dict(orient="records"),
    }

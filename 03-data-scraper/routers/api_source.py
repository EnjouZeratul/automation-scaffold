from __future__ import annotations

import logging
from typing import Any

import httpx
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.api")
normalizer = DataNormalizer()


class ApiSourceRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict[str, str] = {}
    params: dict[str, str] = {}
    pagination: dict[str, Any] | None = None


@router.post("")
async def scrape_api(req: ApiSourceRequest):
    logger.info(f"抓取 API: {req.url}")
    all_data = []
    async with httpx.AsyncClient(timeout=30.0, headers=req.headers) as client:
        page = 1
        max_pages = (req.pagination or {}).get("max_pages", 1)
        page_param = (req.pagination or {}).get("page_param", "page")
        while page <= max_pages:
            params = {**req.params}
            if req.pagination:
                params[page_param] = page
            resp = await client.request(req.method, req.url, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("data", data.get("results", []))
            if not items:
                break
            all_data.extend(items)
            page += 1

    df = normalizer.normalize(pd.DataFrame(all_data)) if all_data else pd.DataFrame()
    logger.info(f"API 抓取完成: {len(df)} 条")
    return {
        "count": len(df),
        "columns": list(df.columns),
        "preview": df.head(10).to_dict(orient="records"),
    }

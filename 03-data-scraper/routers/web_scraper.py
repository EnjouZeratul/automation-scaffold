from __future__ import annotations

import logging
import random
import time
from typing import Any

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from cleaners.normalizer import DataNormalizer

router = APIRouter()
logger = logging.getLogger("scraper.web")
normalizer = DataNormalizer()

try:
    from fake_useragent import UserAgent
    _ua = UserAgent()
except ImportError:
    _ua = None


class WebScrapeRequest(BaseModel):
    url: str
    method: str = "static"  # static | playwright
    selectors: dict[str, str] = {}
    proxy: str = ""
    max_pages: int = 1


def _get_ua() -> str:
    if _ua:
        return _ua.random
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@router.post("")
async def scrape_web(req: WebScrapeRequest):
    logger.info(f"网页抓取: {req.url} (method={req.method})")
    if req.method == "playwright":
        return await _scrape_playwright(req)
    return await _scrape_static(req)


async def _scrape_static(req: WebScrapeRequest) -> dict[str, Any]:
    import httpx
    from bs4 import BeautifulSoup

    all_items = []
    async with httpx.AsyncClient(
        timeout=30.0,
        headers={"User-Agent": _get_ua()},
        proxy=req.proxy or None,
    ) as client:
        for _ in range(1, req.max_pages + 1):
            resp = await client.get(req.url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for field, selector in req.selectors.items():
                for el in soup.select(selector):
                    all_items.append({field: el.get_text(strip=True)})
            time.sleep(random.uniform(1.0, 3.0))

    if all_items:
        df = normalizer.normalize(pd.DataFrame(all_items))
    else:
        df = pd.DataFrame()
    return {"count": len(df), "data": df.to_dict(orient="records")}


async def _scrape_playwright(req: WebScrapeRequest) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        if req.proxy:
            context = await browser.new_context(
                user_agent=_get_ua(), proxy={"server": req.proxy}
            )
        else:
            context = await browser.new_context(user_agent=_get_ua())
        page = await context.new_page()
        await page.goto(req.url, wait_until="networkidle")
        items = []
        for field, selector in req.selectors.items():
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = await el.inner_text()
                items.append({field: text.strip()})
        await browser.close()

    if items:
        df = normalizer.normalize(pd.DataFrame(items))
    else:
        df = pd.DataFrame()
    return {"count": len(df), "data": df.to_dict(orient="records")}

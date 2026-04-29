from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import ScraperSettings
from routers import api_source, csv_source, db_source, web_scraper

logger = logging.getLogger("scraper")

settings = ScraperSettings()
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not settings.api_key:
        return
    if credentials is None or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Scraper service starting")
    yield
    logger.info("Scraper service shutting down")


app = FastAPI(title="Data Scraper", lifespan=lifespan)

app.include_router(api_source.router, prefix="/scrape/api", tags=["api"])
app.include_router(csv_source.router, prefix="/scrape/csv", tags=["csv"])
app.include_router(db_source.router, prefix="/scrape/db", tags=["db"])
app.include_router(web_scraper.router, prefix="/scrape/web", tags=["web"])


@app.get("/health")
async def health():
    return {"status": "ok"}

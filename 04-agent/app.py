from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from shared.config.settings import Settings
from shared.utils.logger import setup_logger

from openclaw.bot import OpenClawBot
from openclaw.callback import parse_dingtalk_callback, parse_feishu_callback
from openclaw.router import parse_message
from tools.bailian_tool import BailianAnalyzeTool
from tools.table_tool import TableQueryTool
from tools.web_search_tool import WebSearchTool
from graph.workflow import AgentWorkflow

logger = setup_logger("agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent service starting")
    yield
    logger.info("Agent service shutting down")


app = FastAPI(title="Automation Agent", lifespan=lifespan)


@app.post("/callback/dingtalk")
async def dingtalk_callback(request: Request):
    msg = await parse_dingtalk_callback(request)
    return await _handle_message(msg)


@app.post("/callback/feishu")
async def feishu_callback(request: Request):
    # 处理 URL 验证（challenge）
    body = await request.json()
    challenge = body.get("challenge")
    if challenge:
        return {"challenge": challenge}
    return await _feishu_event(body)


async def _feishu_event(body: dict):
    msg = parse_feishu_callback(body)
    return await _handle_message(msg)


async def _handle_message(msg: dict):
    parsed = parse_message(msg.get("text", ""))
    if not parsed["content"]:
        return {"ok": True}

    settings = Settings()
    bailian = BailianAnalyzeTool(
        api_key=settings.bailian.api_key,
        base_url=settings.bailian.base_url,
    )
    table = TableQueryTool(settings)
    search = WebSearchTool()
    workflow = AgentWorkflow(bailian, table, search)

    result = await workflow.invoke(parsed["content"])

    bot = OpenClawBot(settings)
    if msg["type"] == "dingtalk":
        await bot.send_message(settings.dingtalk.webhook_url, result)
    else:
        await bot.send_message(settings.feishu.webhook_url, result)

    return {"ok": True, "reply": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8100, reload=True)

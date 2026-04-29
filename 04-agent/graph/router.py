from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    messages: list[dict]
    user_intent: str
    tool_name: str
    tool_result: str
    error: str | None


INTENT_MAP = {
    "分析": "bailian_analyze",
    "情感": "bailian_analyze",
    "分类": "bailian_analyze",
    "查询": "table_query",
    "搜索": "web_search",
    "抓取": "scrape_data",
    "推送": "table_push",
}


def identify_intent(text: str) -> str:
    for keyword, intent in INTENT_MAP.items():
        if keyword in text:
            return intent
    return "bailian_analyze"  # 默认意图

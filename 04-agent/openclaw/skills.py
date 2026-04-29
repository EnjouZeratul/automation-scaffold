from __future__ import annotations

from typing import Any

SKILL_REGISTRY: dict[str, dict] = {}


def register_skill(name: str, description: str):
    def decorator(func):
        SKILL_REGISTRY[name] = {"func": func, "description": description}
        return func

    return decorator


@register_skill("table_query", "查询表格数据")
async def skill_table_query(table_name: str, condition: str = "") -> str:
    return f"查询表格 {table_name}: {condition}"


@register_skill("data_push", "推送数据到表格")
async def skill_data_push(table_name: str, data: str) -> str:
    return f"推送数据到表格 {table_name}"


@register_skill("ai_ask", "AI 问答")
async def skill_ai_ask(question: str) -> str:
    return f"AI 回答: {question}"

from __future__ import annotations

import re

MENTION_RE = re.compile(r"@机器人\s*(.*)", re.DOTALL)


def parse_message(text: str) -> dict:
    """解析用户消息，判断是否 @机器人 并提取指令"""
    match = MENTION_RE.search(text)
    if match:
        return {"is_mention": True, "content": match.group(1).strip()}
    return {"is_mention": False, "content": text.strip()}

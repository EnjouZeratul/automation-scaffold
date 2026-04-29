from __future__ import annotations

from typing import Any

from fastapi import Request


async def parse_dingtalk_callback(request: Request) -> dict[str, Any]:
    body = await request.json()
    return {
        "type": "dingtalk",
        "text": body.get("text", {}).get("content", ""),
        "sender_id": body.get("senderId", ""),
        "conversation_id": body.get("conversationId", ""),
    }


async def parse_feishu_callback(body: dict) -> dict[str, Any]:
    event = body.get("event", {})
    message = event.get("message", {})
    return {
        "type": "feishu",
        "text": message.get("content", "{}"),
        "sender_id": event.get("sender", {}).get("sender_id", {}).get("open_id", ""),
        "message_id": message.get("message_id", ""),
    }

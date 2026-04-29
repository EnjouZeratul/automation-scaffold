from __future__ import annotations

from typing import Any

from shared.config.settings import Settings
from shared.utils.logger import setup_logger

logger = setup_logger("openclaw")


class OpenClawBot:
    """钉钉/飞书双向消息适配"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.platform = settings.spreadsheet_platform

    async def send_message(self, webhook_url: str, text: str):
        url = webhook_url
        if self.platform == "dingtalk":
            sign_key = self.settings.dingtalk.webhook_sign_key
            if sign_key:
                from shared.utils.dingtalk import build_webhook_sign
                ts, sign = build_webhook_sign(sign_key)
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}timestamp={ts}&sign={sign}"
        payload = self._build_payload(text)
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info(f"消息已发送 ({self.platform}): {text[:50]}")

    def _build_payload(self, text: str) -> dict:
        if self.platform == "dingtalk":
            return {"msgtype": "text", "text": {"content": text}}
        return {"msg_type": "text", "content": {"text": text}}

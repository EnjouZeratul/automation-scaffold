from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import httpx
from shared.config.settings import Settings
from shared.utils.logger import setup_logger
from table_ops import TableOperations

logger = setup_logger("watcher")


class TableWatcher:
    def __init__(self, settings: Settings, spreadsheet_token: str, sheet_id: str):
        self.settings = settings
        self.spreadsheet_token = spreadsheet_token
        self.sheet_id = sheet_id
        self.table_ops = TableOperations(settings)
        self._snapshot: str = ""
        self._running = False

    def _compute_hash(self, rows: list) -> str:
        raw = json.dumps(rows, ensure_ascii=False, default=str)
        return hashlib.md5(raw.encode()).hexdigest()

    async def _send_notification(self, message: str):
        if self.settings.spreadsheet_platform == "dingtalk":
            url = self.settings.dingtalk.webhook_url
            sign_key = self.settings.dingtalk.webhook_sign_key
            if sign_key:
                from shared.utils.dingtalk import build_webhook_sign
                ts, sign = build_webhook_sign(sign_key)
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}timestamp={ts}&sign={sign}"
            payload = {"msgtype": "text", "text": {"content": message}}
        else:
            url = self.settings.feishu.webhook_url
            payload = {"msg_type": "text", "content": {"text": message}}

        if not url:
            logger.warning("未配置 Webhook URL，跳过通知")
            return

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10.0)
            resp.raise_for_status()
            logger.info(f"通知已发送: {message[:80]}")

    async def watch(self, interval: int = 30):
        self._running = True
        logger.info(f"开始监听表格变更 (间隔 {interval}s)")
        while self._running:
            try:
                rows = await self.table_ops.get_rows(
                    self.spreadsheet_token, self.sheet_id
                )
                current_hash = self._compute_hash(rows)
                if self._snapshot and current_hash != self._snapshot:
                    await self._send_notification(
                        f"【表格变更通知】表格 {self.spreadsheet_token} 数据已更新"
                    )
                self._snapshot = current_hash
            except Exception as e:
                logger.error(f"监听出错: {e}")
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False

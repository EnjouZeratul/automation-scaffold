from __future__ import annotations

import base64
import hashlib
import hmac
import time
import urllib.parse
from typing import Any

import httpx


def build_webhook_sign(secret: str) -> tuple[int, str]:
    """为钉钉自定义机器人 Webhook 生成签名参数。

    Args:
        secret: 群机器人签名密钥 (SEC 开头)

    Returns:
        (timestamp_milliseconds, url_encoded_signature)
    """
    timestamp = int(time.time() * 1000)
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(digest).decode("utf-8"))
    return timestamp, sign


class DingTalkClient:
    BASE_URL = "https://api.dingtalk.com"

    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self._token: str = ""
        self._token_expire: float = 0

    async def _get_token(self) -> str:
        if time.time() < self._token_expire - 300:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/v1.0/oauth2/token",
                json={"appKey": self.app_key, "appSecret": self.app_secret},
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data["accessToken"]
            self._token_expire = time.time() + data["expireIn"]
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._get_token()
        return {
            "x-acs-dingtalk-access-token": token,
            "Content-Type": "application/json",
        }

    async def create_spreadsheet(self, name: str, folder_id: str = "") -> dict[str, Any]:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/v1.0/drive/spreadsheets",
                headers=headers,
                json={"name": name, "folderId": folder_id},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_values(
        self, spreadsheet_token: str, range: str = ""
    ) -> dict[str, Any]:
        headers = await self._headers()
        params = {"range": range} if range else {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/v1.0/drive/spreadsheets/{spreadsheet_token}/values",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()

    async def batch_update_values(
        self, spreadsheet_token: str, value_range: str, rows: list[list[dict]]
    ) -> dict[str, Any]:
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/v1.0/drive/spreadsheets/{spreadsheet_token}/values:batchUpdate",
                headers=headers,
                json={
                    "valueRange": value_range,
                    "rows": rows,
                },
            )
            resp.raise_for_status()
            return resp.json()

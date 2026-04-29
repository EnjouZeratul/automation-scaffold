from unittest.mock import AsyncMock, patch

import pytest

from shared.utils.dingtalk import DingTalkClient


@pytest.mark.asyncio
async def test_get_token():
    client = DingTalkClient(app_key="test", app_secret="test")

    class MockResponse:
        status_code = 200
        def json(self):
            return {"accessToken": "tok123", "expireIn": 7200}
        def raise_for_status(self):
            pass

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=MockResponse())

    with patch("httpx.AsyncClient", return_value=mock_client):
        token = await client._get_token()
        assert token == "tok123"

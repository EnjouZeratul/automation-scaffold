from unittest.mock import AsyncMock, patch

import pytest

from shared.utils.feishu import FeishuClient


@pytest.mark.asyncio
async def test_get_tenant_token():
    client = FeishuClient(app_id="test", app_secret="test")

    class MockResponse:
        status_code = 200
        def json(self):
            return {"tenant_access_token": "t_tok123", "expire": 7200}
        def raise_for_status(self):
            pass

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=MockResponse())

    with patch("httpx.AsyncClient", return_value=mock_client):
        token = await client._get_tenant_token()
        assert token == "t_tok123"

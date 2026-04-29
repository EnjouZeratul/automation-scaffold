from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from shared.config.settings import Settings
from table_ops import TableOperations


@pytest.mark.asyncio
async def test_create_table_dingtalk():
    settings = Settings(spreadsheet_platform="dingtalk")
    settings.dingtalk.app_key = "k"
    settings.dingtalk.app_secret = "s"
    ops = TableOperations(settings)

    class MockResponse:
        status_code = 200
        def json(self):
            return {"spreadsheetToken": "t"}
        def raise_for_status(self):
            pass

    mock_resp = MockResponse()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as m:
        m.return_value = mock_resp
        with patch.object(ops.client, "_get_token", new_callable=AsyncMock, return_value="tok"):
            result = await ops.create_table("测试表")
            assert result["spreadsheetToken"] == "t"

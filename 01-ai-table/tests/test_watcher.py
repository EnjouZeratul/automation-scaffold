from unittest.mock import AsyncMock, patch

import pytest

from shared.config.settings import Settings
from watcher import TableWatcher


@pytest.mark.asyncio
async def test_send_notification_dingtalk():
    settings = Settings(spreadsheet_platform="dingtalk")
    settings.dingtalk.webhook_url = "https://webhook.test.com"
    watcher = TableWatcher(settings, "token", "sheet")
    class MockResponse:
        status_code = 200
        def raise_for_status(self):
            pass

    mock_resp = MockResponse()
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as m:
        m.return_value = mock_resp
        await watcher._send_notification("测试通知")
        m.assert_called_once()


def test_compute_hash():
    from watcher import TableWatcher
    settings = Settings()
    watcher = TableWatcher(settings, "token", "sheet")
    h1 = watcher._compute_hash([["a", "b"]])
    h2 = watcher._compute_hash([["a", "b"]])
    h3 = watcher._compute_hash([["a", "c"]])
    assert h1 == h2
    assert h1 != h3

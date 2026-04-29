from unittest.mock import AsyncMock, patch

import pytest

from ai_processor import AIProcessor
from shared.config.settings import Settings


@pytest.mark.asyncio
async def test_batch_process():
    settings = Settings()
    settings.bailian.api_key = "test"
    proc = AIProcessor(settings)

    class MockResponse:
        status_code = 200
        def json(self):
            return {"choices": [{"message": {"content": "正面"}}]}
        def raise_for_status(self):
            pass

    mock_resp = MockResponse()
    with patch.object(proc.client._client, "post", new_callable=AsyncMock) as m:
        m.return_value = mock_resp
        results = await proc.batch_process(["很好", "一般"], task="sentiment")
        assert len(results) == 2
        assert all(r == "正面" for r in results)

from unittest.mock import AsyncMock, patch

import pytest

from shared.utils.bailian import BailianClient


class MockResponse:
    status_code = 200
    def json(self):
        return {"choices": [{"message": {"content": " A类 "}}]}
    def raise_for_status(self):
        pass


class MockSentimentResponse:
    status_code = 200
    def json(self):
        return {"choices": [{"message": {"content": " 正面 "}}]}
    def raise_for_status(self):
        pass


@pytest.mark.asyncio
async def test_classify_text():
    client = BailianClient(api_key="test", base_url="https://test.com")
    client._client.post = AsyncMock(return_value=MockResponse())
    result = await client.classify_text("测试文本", ["A类", "B类"])
    assert result == "A类"


@pytest.mark.asyncio
async def test_sentiment_analysis():
    client = BailianClient(api_key="test", base_url="https://test.com")
    client._client.post = AsyncMock(return_value=MockSentimentResponse())
    result = await client.sentiment_analysis("很好")
    assert result == "正面"

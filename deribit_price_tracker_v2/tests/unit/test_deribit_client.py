import pytest
from decimal import Decimal
from aioresponses import aioresponses

from app.infrastructure.deribit_client import AiohttpDeribitClient


class TestAiohttpDeribitClient:
    @pytest.mark.asyncio
    async def test_fetch_index_price_success(self):
        client = AiohttpDeribitClient("https://test.deribit.com/api/v2")

        with aioresponses() as mocked:
            mocked.get(
                "https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd",
                payload={"result": {"index_price": "50000.50"}}
            )

            result = await client.fetch_index_price("btc_usd")

            assert result == Decimal("50000.50")

    @pytest.mark.asyncio
    async def test_fetch_index_price_empty_result(self):
        client = AiohttpDeribitClient("https://test.deribit.com/api/v2")

        with aioresponses() as mocked:
            mocked.get(
                "https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd",
                payload={"result": {}}
            )

            result = await client.fetch_index_price("btc_usd")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_index_price_api_error(self):
        client = AiohttpDeribitClient("https://test.deribit.com/api/v2")

        with aioresponses() as mocked:
            mocked.get(
                "https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd",
                status=500
            )

            with pytest.raises(Exception):
                await client.fetch_index_price("btc_usd")

    def test_get_index_price_sync_wrapper(self):
        client = AiohttpDeribitClient("https://test.deribit.com/api/v2")

        with aioresponses() as mocked:
            mocked.get(
                "https://test.deribit.com/api/v2/public/get_index_price?index_name=eth_usd",
                payload={"result": {"index_price": "3000.00"}}
            )

            result = client.get_index_price("eth_usd")

            assert result == Decimal("3000.00")

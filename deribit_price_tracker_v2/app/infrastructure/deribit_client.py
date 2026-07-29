import asyncio
from typing import Optional
from decimal import Decimal

import aiohttp

from app.domain.interfaces import DeribitPriceClient


class AiohttpDeribitClient(DeribitPriceClient):
    """Асинхронный клиент для Deribit на базе aiohttp.

    Предоставляет async-метод для гибкости и sync-обертку
    для совместимости с Celery (синхронный контекст).
    """

    def __init__(self, base_url: str):
        self._base_url = base_url

    async def fetch_index_price(self, ticker: str) -> Optional[Decimal]:
        url = f"{self._base_url}/public/get_index_price"
        params = {"index_name": ticker}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("result") and "index_price" in data["result"]:
                    return Decimal(str(data["result"]["index_price"]))
                return None

    def get_index_price(self, ticker: str) -> Optional[Decimal]:
        """Синхронная обертка для использования в Celery и DI."""
        return asyncio.run(self.fetch_index_price(ticker))

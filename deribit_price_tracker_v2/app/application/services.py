from decimal import Decimal
from typing import List, Optional
import time

from app.domain.entities import PriceRecord
from app.domain.interfaces import PriceRepository, DeribitPriceClient


class PriceTrackingService:
    """Сервис прикладного уровня. Зависит только от абстракций (интерфейсов)."""

    def __init__(
        self,
        price_client: DeribitPriceClient,
        repository: PriceRepository
    ):
        self._price_client = price_client
        self._repository = repository

    def fetch_and_save(self, ticker: str) -> Optional[PriceRecord]:
        """Получает цену с биржи и сохраняет в БД."""
        price = self._price_client.get_index_price(ticker)
        if price is None:
            return None

        record = PriceRecord(
            id=None,
            ticker=ticker,
            price=price,
            timestamp=int(time.time()),
            created_at=None
        )
        return self._repository.save(record)

    def get_all_records(self, ticker: str) -> List[PriceRecord]:
        return self._repository.get_all_by_ticker(ticker)

    def get_last_record(self, ticker: str) -> Optional[PriceRecord]:
        return self._repository.get_last_by_ticker(ticker)

    def get_filtered_records(
        self, ticker: str, start_date: Optional[int], end_date: Optional[int]
    ) -> List[PriceRecord]:
        return self._repository.get_by_ticker_and_date_range(
            ticker, start_date, end_date
        )

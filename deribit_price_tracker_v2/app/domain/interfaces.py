from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from app.domain.entities import PriceRecord


class PriceRepository(ABC):
    """Абстракция репозитория. Реализация скрыта за интерфейсом."""

    @abstractmethod
    def save(self, record: PriceRecord) -> PriceRecord:
        raise NotImplementedError

    @abstractmethod
    def get_all_by_ticker(self, ticker: str) -> List[PriceRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_last_by_ticker(self, ticker: str) -> Optional[PriceRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_by_ticker_and_date_range(
        self, ticker: str, start_date: Optional[int], end_date: Optional[int]
    ) -> List[PriceRecord]:
        raise NotImplementedError


class DeribitPriceClient(ABC):
    """Абстракция клиента Deribit. Позволяет подменить реализацию в тестах."""

    @abstractmethod
    def get_index_price(self, ticker: str) -> Optional[Decimal]:
        raise NotImplementedError

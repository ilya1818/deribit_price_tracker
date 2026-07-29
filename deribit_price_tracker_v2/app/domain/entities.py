from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime


@dataclass(frozen=True)
class PriceRecord:
    """Чистая доменная сущность. Не зависит от инфраструктуры."""
    id: int | None
    ticker: str
    price: Decimal
    timestamp: int
    created_at: datetime | None

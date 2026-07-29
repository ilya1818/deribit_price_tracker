from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class PriceRecordResponse(BaseModel):
    id: int
    ticker: str
    price: Decimal
    timestamp: int
    created_at: datetime | None

    class Config:
        from_attributes = True


class PriceListResponse(BaseModel):
    ticker: str
    count: int
    data: list[PriceRecordResponse]

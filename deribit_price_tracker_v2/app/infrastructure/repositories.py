from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.domain.entities import PriceRecord
from app.domain.interfaces import PriceRepository
from app.infrastructure.models import PriceRecordORM


class PostgresPriceRepository(PriceRepository):
    """Реализация репозитория на PostgreSQL через SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, record: PriceRecord) -> PriceRecord:
        orm_record = PriceRecordORM(
            ticker=record.ticker,
            price=record.price,
            timestamp=record.timestamp
        )
        self._session.add(orm_record)
        self._session.commit()
        self._session.refresh(orm_record)
        return self._to_entity(orm_record)

    def _to_entity(self, orm_record: PriceRecordORM) -> PriceRecord:
        return PriceRecord(
            id=orm_record.id,
            ticker=orm_record.ticker,
            price=orm_record.price,
            timestamp=orm_record.timestamp,
            created_at=orm_record.created_at
        )

    def get_all_by_ticker(self, ticker: str) -> List[PriceRecord]:
        records = self._session.query(PriceRecordORM).filter(
            PriceRecordORM.ticker == ticker
        ).order_by(desc(PriceRecordORM.timestamp)).all()
        return [self._to_entity(r) for r in records]

    def get_last_by_ticker(self, ticker: str) -> Optional[PriceRecord]:
        record = self._session.query(PriceRecordORM).filter(
            PriceRecordORM.ticker == ticker
        ).order_by(desc(PriceRecordORM.timestamp)).first()
        return self._to_entity(record) if record else None

    def get_by_ticker_and_date_range(
        self, ticker: str, start_date: Optional[int], end_date: Optional[int]
    ) -> List[PriceRecord]:
        query = self._session.query(PriceRecordORM).filter(
            PriceRecordORM.ticker == ticker
        )
        if start_date is not None:
            query = query.filter(PriceRecordORM.timestamp >= start_date)
        if end_date is not None:
            query = query.filter(PriceRecordORM.timestamp <= end_date)
        records = query.order_by(desc(PriceRecordORM.timestamp)).all()
        return [self._to_entity(r) for r in records]

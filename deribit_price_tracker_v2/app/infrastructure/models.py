from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.infrastructure.database import Base


class PriceRecordORM(Base):
    """ORM-модель SQLAlchemy. Отделена от доменной сущности."""
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    price = Column(Numeric(24, 8), nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import PriceRecord
from app.schemas import PriceRecordResponse, PriceListResponse

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/all", response_model=PriceListResponse)
def get_all_prices(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    db: Session = Depends(get_db)
):
    """
    Получение всех сохраненных данных по указанной валюте.
    """
    records = db.query(PriceRecord).filter(
        PriceRecord.ticker == ticker
    ).order_by(desc(PriceRecord.timestamp)).all()

    return PriceListResponse(
        ticker=ticker,
        count=len(records),
        data=records
    )


@router.get("/last", response_model=PriceRecordResponse)
def get_last_price(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    db: Session = Depends(get_db)
):
    """
    Получение последней сохраненной цены валюты.
    """
    record = db.query(PriceRecord).filter(
        PriceRecord.ticker == ticker
    ).order_by(desc(PriceRecord.timestamp)).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"Данные для тикера {ticker} не найдены")

    return record


@router.get("/filter", response_model=PriceListResponse)
def get_prices_with_filter(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    start_date: Optional[int] = Query(None, description="Начальная дата в UNIX timestamp"),
    end_date: Optional[int] = Query(None, description="Конечная дата в UNIX timestamp"),
    db: Session = Depends(get_db)
):
    """
    Получение цены валюты с фильтром по дате (UNIX timestamp).

    - start_date: включительно
    - end_date: включительно
    """
    query = db.query(PriceRecord).filter(PriceRecord.ticker == ticker)

    if start_date is not None:
        query = query.filter(PriceRecord.timestamp >= start_date)

    if end_date is not None:
        query = query.filter(PriceRecord.timestamp <= end_date)

    records = query.order_by(desc(PriceRecord.timestamp)).all()

    return PriceListResponse(
        ticker=ticker,
        count=len(records),
        data=records
    )

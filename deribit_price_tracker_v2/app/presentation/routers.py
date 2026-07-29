from fastapi import APIRouter, Depends, Query, HTTPException

from app.application.services import PriceTrackingService
from app.presentation.schemas import PriceRecordResponse, PriceListResponse
from app.presentation.dependencies import get_price_service

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/all", response_model=PriceListResponse)
def get_all_prices(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    service: PriceTrackingService = Depends(get_price_service)
):
    """Получение всех сохраненных данных по указанной валюте."""
    records = service.get_all_records(ticker)
    return PriceListResponse(ticker=ticker, count=len(records), data=records)


@router.get("/last", response_model=PriceRecordResponse)
def get_last_price(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    service: PriceTrackingService = Depends(get_price_service)
):
    """Получение последней сохраненной цены валюты."""
    record = service.get_last_record(ticker)
    if not record:
        raise HTTPException(status_code=404, detail=f"Данные для тикера {ticker} не найдены")
    return record


@router.get("/filter", response_model=PriceListResponse)
def get_prices_with_filter(
    ticker: str = Query(..., description="Тикер валюты, например btc_usd или eth_usd"),
    start_date: int | None = Query(None, description="Начальная дата в UNIX timestamp"),
    end_date: int | None = Query(None, description="Конечная дата в UNIX timestamp"),
    service: PriceTrackingService = Depends(get_price_service)
):
    """Получение цены валюты с фильтром по дате (UNIX timestamp)."""
    records = service.get_filtered_records(ticker, start_date, end_date)
    return PriceListResponse(ticker=ticker, count=len(records), data=records)

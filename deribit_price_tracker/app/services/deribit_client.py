import requests
import time
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class DeribitClient:
    def __init__(self):
        self.base_url = settings.deribit_base_url

    def get_index_price(self, ticker: str) -> Optional[float]:
        """
        Получает index price для указанного тикера с Deribit.

        Args:
            ticker: Название индекса, например "btc_usd" или "eth_usd"

        Returns:
            Текущая цена индекса или None в случае ошибки
        """
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": ticker}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("result"):
                price = data["result"]["index_price"]
                logger.info(f"Получена цена для {ticker}: {price}")
                return float(price)
            else:
                logger.error(f"Пустой результат от API для {ticker}")
                return None

        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к Deribit для {ticker}: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Ошибка парсинга ответа для {ticker}: {e}")
            return None


def fetch_and_save_price(ticker: str, db_session) -> bool:
    """
    Забирает цену с Deribit и сохраняет в БД.

    Args:
        ticker: Тикер валюты
        db_session: Сессия SQLAlchemy

    Returns:
        True если успешно, иначе False
    """
    from app.models import PriceRecord

    client = DeribitClient()
    price = client.get_index_price(ticker)

    if price is None:
        return False

    timestamp = int(time.time())

    record = PriceRecord(
        ticker=ticker,
        price=price,
        timestamp=timestamp
    )

    db_session.add(record)
    db_session.commit()

    logger.info(f"Сохранена запись: {ticker} = {price} @ {timestamp}")
    return True

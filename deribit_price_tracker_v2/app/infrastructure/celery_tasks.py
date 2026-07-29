import logging

from app.config import Settings
from app.infrastructure.celery_app import create_celery_app
from app.infrastructure.database import Database
from app.infrastructure.deribit_client import AiohttpDeribitClient
from app.infrastructure.repositories import PostgresPriceRepository
from app.application.services import PriceTrackingService

logger = logging.getLogger(__name__)

settings = Settings()
celery_app = create_celery_app(settings)


@celery_app.task(bind=True, max_retries=3)
def fetch_btc_price(self):
    return _fetch_and_save("btc_usd")


@celery_app.task(bind=True, max_retries=3)
def fetch_eth_price(self):
    return _fetch_and_save("eth_usd")


def _fetch_and_save(ticker: str):
    """Вспомогательная функция для избежания дублирования.

    Создает свежие инстансы зависимостей для каждого вызова,
    чтобы избежать проблем с состоянием между задачами.
    """
    database = Database(settings.database_url)
    session = database.get_session()
    try:
        client = AiohttpDeribitClient(settings.deribit_base_url)
        repository = PostgresPriceRepository(session)
        service = PriceTrackingService(client, repository)

        result = service.fetch_and_save(ticker)
        if result is None:
            logger.warning(f"Не удалось получить цену {ticker}, retry через 10 сек")
            raise fetch_btc_price.retry(countdown=10)

        logger.info(f"Сохранена цена {ticker}: {result.price}")
        return {"ticker": ticker, "price": str(result.price), "status": "success"}
    except Exception as exc:
        logger.error(f"Ошибка при получении цены {ticker}: {exc}")
        raise fetch_btc_price.retry(exc=exc, countdown=10)
    finally:
        session.close()

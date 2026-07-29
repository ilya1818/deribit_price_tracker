import logging
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.deribit_client import fetch_and_save_price

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def fetch_btc_price(self):
    """
    Задача Celery для получения и сохранения цены BTC/USD.
    """
    db = SessionLocal()
    try:
        success = fetch_and_save_price("btc_usd", db)
        if not success:
            logger.warning("Не удалось получить цену BTC, будет выполнен retry")
            raise self.retry(countdown=10)
        return {"ticker": "btc_usd", "status": "success"}
    except Exception as exc:
        logger.error(f"Ошибка в задаче fetch_btc_price: {exc}")
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def fetch_eth_price(self):
    """
    Задача Celery для получения и сохранения цены ETH/USD.
    """
    db = SessionLocal()
    try:
        success = fetch_and_save_price("eth_usd", db)
        if not success:
            logger.warning("Не удалось получить цену ETH, будет выполнен retry")
            raise self.retry(countdown=10)
        return {"ticker": "eth_usd", "status": "success"}
    except Exception as exc:
        logger.error(f"Ошибка в задаче fetch_eth_price: {exc}")
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()

from celery import Celery
from app.config import settings

celery_app = Celery(
    "deribit_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["celery_worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-btc-price-every-minute": {
            "task": "celery_worker.tasks.fetch_btc_price",
            "schedule": 60.0,  # каждые 60 секунд
        },
        "fetch-eth-price-every-minute": {
            "task": "celery_worker.tasks.fetch_eth_price",
            "schedule": 60.0,
        },
    },
)

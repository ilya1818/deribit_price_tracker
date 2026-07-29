from celery import Celery

from app.config import Settings


def create_celery_app(settings: Settings) -> Celery:
    """Фабрика для создания Celery приложения.

    Использует PostgreSQL как брокер и backend —
    позволяет обойтись без отдельного Redis-контейнера.
    """
    celery_app = Celery(
        "deribit_tracker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.infrastructure.celery_tasks"]
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "fetch-btc-price-every-minute": {
                "task": "app.infrastructure.celery_tasks.fetch_btc_price",
                "schedule": 60.0,
            },
            "fetch-eth-price-every-minute": {
                "task": "app.infrastructure.celery_tasks.fetch_eth_price",
                "schedule": 60.0,
            },
        },
    )

    return celery_app

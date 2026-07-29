from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings
from app.infrastructure.database import Database
from app.infrastructure.deribit_client import AiohttpDeribitClient
from app.infrastructure.repositories import PostgresPriceRepository
from app.application.services import PriceTrackingService


def get_settings() -> Settings:
    return Settings()


def get_database(settings: Settings = Depends(get_settings)) -> Database:
    return Database(settings.database_url)


def get_db_session(database: Database = Depends(get_database)):
    session = database.get_session()
    try:
        yield session
    finally:
        session.close()


def get_price_service(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session)
) -> PriceTrackingService:
    client = AiohttpDeribitClient(settings.deribit_base_url)
    repository = PostgresPriceRepository(session)
    return PriceTrackingService(client, repository)

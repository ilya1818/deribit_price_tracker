from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация приложения. Создается по требованию через DI."""

    database_url: str = "postgresql://postgres:postgres@db:5432/deribit_prices"
    deribit_base_url: str = "https://www.deribit.com/api/v2"

    @property
    def celery_broker_url(self) -> str:
        return f"sqla+{self.database_url}"

    @property
    def celery_result_backend(self) -> str:
        return f"db+{self.database_url}"

    class Config:
        env_file = ".env"

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@db:5432/deribit_prices"
    redis_url: str = "redis://redis:6379/0"
    deribit_base_url: str = "https://www.deribit.com/api/v2"

    class Config:
        env_file = ".env"


settings = Settings()

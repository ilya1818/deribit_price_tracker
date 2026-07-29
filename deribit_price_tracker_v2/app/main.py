from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import Settings
from app.infrastructure.database import Database
from app.presentation.routers import router as prices_router

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = Database(settings.database_url)
    database.create_tables()
    yield


app = FastAPI(
    title="Deribit Price Tracker API",
    description="API для получения и хранения цен криптовалют с биржи Deribit",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(prices_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

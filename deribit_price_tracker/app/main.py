from fastapi import FastAPI
from app.database import engine, Base
from app.api import prices

# Создание таблиц при старте (для простоты разработки)
# В продакшене рекомендуется использовать Alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Deribit Price Tracker API",
    description="API для получения и хранения цен криптовалют с биржи Deribit",
    version="1.0.0"
)

app.include_router(prices.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

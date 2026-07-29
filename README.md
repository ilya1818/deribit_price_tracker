# Deribit Price Tracker

Тестовое задание на позицию Junior Backend Developer.

Сервис для периодического сбора цен криптовалют (BTC/USD, ETH/USD) с биржи Deribit и предоставления REST API для доступа к сохраненным данным.

## Стек технологий

- **FastAPI** — веб-фреймворк для API
- **SQLAlchemy** + **PostgreSQL** — ORM и реляционная БД
- **aiohttp** — асинхронный HTTP-клиент для Deribit
- **Celery** (с PostgreSQL брокером) — периодические задачи
- **Alembic** — миграции БД
- **pytest** + **aioresponses** — unit-тесты
- **Docker** + **Docker Compose** — контейнеризация
- **Supervisor** — управление процессами внутри контейнера

## Архитектура

Проект построен по принципам **Clean Architecture** (Layered Architecture):

```
app/
├── domain/                    # Слой домена (бизнес-логика)
│   ├── entities.py            # Чистые сущности (PriceRecord)
│   └── interfaces.py          # Абстрактные интерфейсы (ABC)
├── application/               # Слой приложения (use cases)
│   └── services.py            # PriceTrackingService
├── infrastructure/            # Слой инфраструктуры
│   ├── database.py            # SQLAlchemy Database класс
│   ├── models.py              # ORM-модели
│   ├── repositories.py        # PostgresPriceRepository
│   ├── deribit_client.py      # AiohttpDeribitClient
│   ├── celery_app.py          # Фабрика Celery
│   └── celery_tasks.py        # Задачи Celery
├── presentation/              # Слой представления
│   ├── schemas.py             # Pydantic схемы
│   ├── dependencies.py        # Dependency Injection
│   └── routers.py             # FastAPI роутеры
└── main.py                    # Точка входа
```

### Почему Clean Architecture?

- **Независимость слоев**: домен не зависит от FastAPI, SQLAlchemy или aiohttp
- **Тестируемость**: бизнес-логика тестируется без БД и HTTP-клиентов (моки)
- **Гибкость**: можно заменить PostgreSQL на MongoDB или aiohttp на httpx, не меняя бизнес-логику

## API Endpoints

Все методы `GET`, обязательный query-параметр `ticker`.

| Endpoint | Описание | Параметры |
|----------|----------|-----------|
| `GET /prices/all?ticker=btc_usd` | Все сохраненные данные по валюте | `ticker` (required) |
| `GET /prices/last?ticker=btc_usd` | Последняя сохраненная цена | `ticker` (required) |
| `GET /prices/filter?ticker=btc_usd&start_date=1700000000&end_date=1700003600` | Цены с фильтром по дате | `ticker` (required), `start_date`, `end_date` — UNIX timestamp |

## Design Decisions

### 1. Clean Architecture / Layered Architecture
Проект разделен на 4 слоя: **domain**, **application**, **infrastructure**, **presentation**.
- Domain содержит только чистые сущности и абстрактные интерфейсы
- Application содержит бизнес-логику (`PriceTrackingService`), зависящую только от абстракций
- Infrastructure содержит конкретные реализации (SQLAlchemy, aiohttp, Celery)
- Presentation содержит FastAPI-специфичный код

**Преимущества**: легко тестировать, легко менять реализации, код не превращается в "спагетти".

### 2. Отсутствие глобальных переменных
Вместо глобальных `engine`, `SessionLocal`, `settings` используется:
- Класс `Database`, инкапсулирующий подключение к БД
- Фабрика `create_celery_app()` для создания Celery
- Dependency Injection в FastAPI через `Depends()`
- Каждая Celery-задача создает свежие инстансы зависимостей

Это предотвращает проблемы с состоянием, race conditions и упрощает тестирование.

### 3. aiohttp для HTTP-клиента
Вместо `requests` используется `aiohttp`:
- **Асинхронность**: не блокирует event loop при ожидании ответа от Deribit
- **Производительность**: при масштабировании на N тикеров запросы можно выполнять параллельно
- **Современный стандарт**: async/await — де-факто стандарт для Python backend

Синхронная обертка `get_index_price()` позволяет использовать клиент в Celery (который работает в синхронном контексте).

### 4. PostgreSQL как брокер Celery
Вместо отдельного Redis-контейнера используется PostgreSQL:
- **Соответствие требованию**: "два контейнера" — приложение и БД
- **Простота**: не нужен третий сервис
- **Достаточность**: для 2 запросов в минуту производительности PostgreSQL-брокера более чем достаточно

### 5. Supervisor внутри контейнера
В одном контейнере `app` запускаются 3 процесса:
- **uvicorn** — FastAPI сервер
- **celery worker** — обработка задач
- **celery beat** — планировщик периодических задач

Это позволяет уложиться в 2 контейнера, сохранив функциональность.

### 6. Абстрактные классы (ABC) и Dependency Injection
- `PriceRepository` и `DeribitPriceClient` — абстрактные интерфейсы
- `PriceTrackingService` зависит от интерфейсов, а не от конкретных классов
- В тестах реализации заменяются на моки через `unittest.mock.create_autospec`

### 7. Decimal вместо float для цен
- **Точность**: криптовалютные цены требуют точности, float накапливает ошибки округления
- **Финансовые расчеты**: при дальнейшем развитии проекта точность критична

### 8. Отделение ORM-модели от доменной сущности
- `PriceRecordORM` (SQLAlchemy) и `PriceRecord` (dataclass) — разные классы
- Репозиторий отвечает за маппинг между ними (`_to_entity()`)
- Доменная сущность `frozen=True` — иммутабельна, без побочных эффектов

## Развертывание

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd deribit_price_tracker

# 2. Запустить (всего 2 контейнера: app + db)
docker-compose up --build -d

# 3. Проверить статус
docker-compose ps

# 4. API доступно по адресу
curl http://localhost:8000/health
```

### Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# Получить все данные по BTC
curl "http://localhost:8000/prices/all?ticker=btc_usd"

# Получить последнюю цену ETH
curl "http://localhost:8000/prices/last?ticker=eth_usd"

# Фильтр по дате (последний час)
NOW=$(date +%s)
HOUR_AGO=$((NOW - 3600))
curl "http://localhost:8000/prices/filter?ticker=btc_usd&start_date=${HOUR_AGO}&end_date=${NOW}"
```

## Unit-тесты

### Запуск тестов локально

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить тесты
pytest tests/ -v
```

### Структура тестов

```
tests/
├── conftest.py                    # Фикстуры pytest
└── unit/
    ├── test_services.py             # Тесты бизнес-логики (моки)
    ├── test_api.py                  # Тесты API-эндпоинтов (моки сервиса)
    └── test_deribit_client.py     # Тесты aiohttp-клиента (aioresponses)
```

### Что тестируется

| Тест | Что проверяется |
|------|-----------------|
| `test_fetch_and_save_success` | Сервис получает цену и сохраняет в репозиторий |
| `test_fetch_and_save_when_api_returns_none` | Корректная обработка отсутствия данных |
| `test_get_all_records` | Получение всех записей по тикеру |
| `test_get_last_record` | Получение последней записи |
| `test_get_filtered_records` | Фильтрация по диапазону дат |
| `test_get_all_prices` | API-эндпоинт /prices/all |
| `test_get_last_price_success` | API-эндпоинт /prices/last |
| `test_get_last_price_not_found` | 404 при отсутствии данных |
| `test_missing_ticker_parameter` | Валидация обязательного параметра |
| `test_fetch_index_price_success` | aiohttp клиент парсит ответ Deribit |
| `test_fetch_index_price_api_error` | Обработка HTTP 500 от Deribit |
| `test_get_index_price_sync_wrapper` | Синхронная обертка async-метода |

## Миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/deribit_prices` |
| `DERIBIT_BASE_URL` | Базовый URL Deribit API | `https://www.deribit.com/api/v2` |

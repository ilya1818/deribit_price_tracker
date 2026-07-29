# Deribit Price Tracker

Тестовое задание на позицию Junior Backend Developer.

Сервис для периодического сбора цен криптовалют (BTC/USD, ETH/USD) с биржи Deribit и предоставления API для доступа к сохраненным данным.

## Стек технологий

- **FastAPI** — веб-фреймворк для API
- **SQLAlchemy** + **PostgreSQL** — ORM и реляционная БД
- **Celery** + **Redis** — периодические задачи и брокер сообщений
- **Alembic** — миграции БД
- **Docker** + **Docker Compose** — контейнеризация
- **Pydantic Settings** — управление конфигурацией

## Архитектура

```
deribit_price_tracker/
├── app/
│   ├── api/prices.py          # Эндпоинты FastAPI
│   ├── services/
│   │   └── deribit_client.py  # Клиент для Deribit API
│   ├── config.py              # Настройки приложения
│   ├── database.py            # Подключение к БД
│   ├── models.py              # SQLAlchemy модели
│   ├── schemas.py             # Pydantic схемы
│   ├── main.py                # Точка входа FastAPI
│   └── celery_app.py          # Конфигурация Celery
├── celery_worker/
│   └── tasks.py               # Celery-задачи
├── alembic/                   # Миграции
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API Endpoints

Все методы `GET`, обязательный query-параметр `ticker`.

| Endpoint | Описание | Параметры |
|----------|----------|-----------|
| `GET /prices/all?ticker=btc_usd` | Все сохраненные данные по валюте | `ticker` (required) |
| `GET /prices/last?ticker=btc_usd` | Последняя сохраненная цена | `ticker` (required) |
| `GET /prices/filter?ticker=btc_usd&start_date=1700000000&end_date=1700003600` | Цены с фильтром по дате | `ticker` (required), `start_date` (optional), `end_date` (optional) — UNIX timestamp |

## Design Decisions

### 1. Синхронный SQLAlchemy вместо async
Для junior-level проекта выбран синхронный подход:
- **Простота**: не требуется разбираться с `async_session`, `await` в SQLAlchemy 2.0
- **Celery совместимость**: Celery worker не полностью async-friendly, sync сессии проще интегрировать
- **Производительность**: для текущей нагрузки (2 запроса в минуту) синхронности более чем достаточно

### 2. Отдельные задачи для BTC и ETH
Вместо одной задачи, которая забирает обе цены, созданы две независимые задачи:
- **Изоляция ошибок**: если Deribit недоступен для ETH, BTC всё равно сохранится
- **Гранулярный retry**: каждая задача имеет свой счетчик retry (max 3)
- **Масштабируемость**: при добавлении новых тикеров не нужно менять код задач

### 3. UNIX timestamp вместо datetime
В задании явно указано сохранять время в UNIX timestamp:
- **Универсальность**: легко конвертировать в любой часовой пояс
- **Фильтрация**: простое сравнение чисел в БД
- **API-совместимость**: Deribit и многие крипто-API используют UNIX timestamp

### 4. Numeric(24,8) для цен
Используется `Decimal`/`Numeric` вместо `Float`:
- **Точность**: криптовалютные цены требуют точности, float накапливает ошибки округления
- **Финансовые расчеты**: при дальнейшем развитии проекта точность критична

### 5. Docker Compose с healthcheck
PostgreSQL имеет healthcheck перед запуском API и Celery:
- **Надежность**: сервисы не падают при старте из-за недоступности БД
- **Порядок запуска**: API стартует только после готовности PostgreSQL

### 6. Pydantic Settings
Конфигурация через environment variables с валидацией:
- **12-factor app**: конфигурация в env, не в коде
- **Типизация**: автоматическая валидация типов при старте
- **Переиспользование**: одни настройки используются и в API, и в Celery

## Развертывание

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd deribit_price_tracker

# 2. Запустить все сервисы
docker-compose up --build -d

# 3. Проверить статус
docker-compose ps

# 4. API доступно по адресу
curl http://localhost:8000/health
```

### Локальная разработка (без Docker)

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить PostgreSQL и Redis (например, через Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=deribit_prices postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine

# 4. Применить миграции
alembic upgrade head

# 5. Запустить API
uvicorn app.main:app --reload

# 6. В отдельном терминале запустить Celery worker
celery -A app.celery_app worker --loglevel=info

# 7. В еще одном терминале запустить Celery beat
celery -A app.celery_app beat --loglevel=info
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

## Миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание изменений"

# Применить миграции
alembic upgrade head

# Откатить на одну миграцию
alembic downgrade -1
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/deribit_prices` |
| `REDIS_URL` | URL подключения к Redis | `redis://redis:6379/0` |
| `DERIBIT_BASE_URL` | Базовый URL Deribit API | `https://www.deribit.com/api/v2` |

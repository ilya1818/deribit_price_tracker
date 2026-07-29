from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class Database:
    """Инкапсулирует подключение к БД. Не использует глобальные переменные."""

    def __init__(self, database_url: str):
        self._engine = create_engine(database_url)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def get_session(self) -> Session:
        return self._session_factory()

    def session_scope(self):
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

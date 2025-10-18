import os

from sqlmodel import SQLModel, create_engine


def _build_engine():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        if database_url.startswith("postgresqlpsycopg://"):
            database_url = database_url.replace("postgresqlpsycopg://", "postgresql+psycopg://", 1)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return create_engine(database_url, echo=False)

    sqlite_file_name = "studyquest.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    return create_engine(sqlite_url, echo=False)


engine = _build_engine()


def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

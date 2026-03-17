from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.resolved_database_url,
    echo=settings.app_env == "development",
    pool_size=5,
    max_overflow=10,
)

SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── History DB (vitamin_history) ───────────────────────────────────────────────

if settings.history_database_url:
    history_engine = create_async_engine(
        settings.history_database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )
    HistorySessionLocal = async_sessionmaker(
        history_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
else:
    history_engine = None
    HistorySessionLocal = None


async def get_history_db() -> AsyncSession | None:
    if HistorySessionLocal is None:
        yield None
        return
    async with HistorySessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

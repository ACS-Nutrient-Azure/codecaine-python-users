from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 비동기 DB 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",  # 개발 환경에서는 SQL 로그 출력
    pool_size=5,
    max_overflow=10,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """모든 모델이 상속받는 베이스 클래스"""
    pass


async def get_db() -> AsyncSession:
    """
    API 엔드포인트에서 DB 세션을 주입받기 위한 의존성.
    
    사용법:
        @router.get("/me")
        async def get_profile(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

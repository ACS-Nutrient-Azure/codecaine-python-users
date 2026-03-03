from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.app_name,
    description="영양제 추천 서비스 - 마이페이지 마이크로서비스",
    version="1.0.0",
    # 운영 환경에서는 docs 비활성화
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
)

# CORS 설정 (프론트엔드 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router)


@app.get("/health", tags=["헬스체크"])
async def health_check():
    """
    AWS ECS / ALB 헬스체크용 엔드포인트.
    MSA에서 각 서비스의 상태를 모니터링할 때 사용.
    """
    return {"status": "ok", "service": settings.app_name}

from fastapi import APIRouter
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.users import supplement_router

api_router = APIRouter(prefix="/api")
api_router.include_router(users_router)
api_router.include_router(supplement_router)

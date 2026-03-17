from fastapi import APIRouter
from app.api.endpoints.users import router as users_router
from app.api.endpoints.users import supplement_router
from app.api.endpoints.codef import router as codef_router

api_router = APIRouter(prefix="/api")
api_router.include_router(supplement_router)
api_router.include_router(users_router)
api_router.include_router(codef_router)

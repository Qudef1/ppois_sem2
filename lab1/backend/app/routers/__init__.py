from fastapi import APIRouter

from app.routers.info import router as info_router
from app.routers.staff import router as staff_router
from app.routers.user import router as user_router


def build_api_router() -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(staff_router)
    api_router.include_router(user_router)
    api_router.include_router(info_router)
    return api_router

from fastapi import APIRouter

from app.routers.rest.health import router as health_router


def provide_api_v1_router() -> APIRouter:
    router = APIRouter()

    router.include_router(health_router, prefix="/health", tags=["health"])

    return router

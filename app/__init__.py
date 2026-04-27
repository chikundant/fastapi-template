from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.settings import Settings
from app.db.session import close_db_pool, provide_async_db_pool
from app.routers.rest import provide_api_v1_router

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await provide_async_db_pool(settings.db)

    yield

    await close_db_pool(app)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)
    app.include_router(provide_api_v1_router(), prefix="/api/v1")
    return app


app = create_app()

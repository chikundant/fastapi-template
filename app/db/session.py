import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from starlette.requests import HTTPConnection

from app.core.settings import DBSettings


class AsyncDBPoolProvisionError(Exception):
    pass


def _db_json(obj: Any) -> str:
    if isinstance(obj, datetime):
        return f"{obj.isoformat()}Z"
    return obj


async def provide_async_db_pool(  # type: ignore
    settings: DBSettings, max_retries: int = 3, retry_interval: int = 2
) -> AsyncEngine:
    for attempt in range(max_retries + 1):
        try:
            pool = create_async_engine(
                settings.ASYNC_DSN,
                echo=settings.ECHO,
                pool_size=settings.POOL_SIZE,
                max_overflow=settings.POOL_OVERFLOW,
                json_serializer=lambda obj: json.dumps(obj, default=_db_json),
                connect_args={"timeout": 5},
            )
            async with pool.begin() as conn:
                await conn.execute(text("SELECT 1;"))

            return pool
        except Exception as exc:
            if attempt < max_retries:
                await asyncio.sleep(retry_interval)
            else:
                raise AsyncDBPoolProvisionError("failed to connect to db") from exc


async def close_db_pool(app: FastAPI) -> None:
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.dispose()


def _get_db_pool(request: HTTPConnection) -> AsyncEngine:
    return request.app.state.db_pool


async def get_session(
    pool: AsyncEngine = Depends(_get_db_pool),
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(pool, expire_on_commit=False) as session:
        yield session

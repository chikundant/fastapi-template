from abc import ABC
from typing import Generic, Type, TypeVar

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.exceptions.repos import (
    ForeignKeyViolationException,
    NotFoundException,
    NotNullViolationException,
    UniqueViolationException,
)
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
NotFoundExcType = TypeVar("NotFoundExcType", bound=NotFoundException)


INTEGRITY_ERRORS = {
    "23505": UniqueViolationException,
    "23502": NotNullViolationException,
    "23503": ForeignKeyViolationException,
}


class BaseRepo(ABC, Generic[ModelType, NotFoundExcType]):
    model: Type[ModelType]
    not_found_exception: Type[NotFoundExcType]

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def create(self, obj: ModelType, refresh: bool = True) -> ModelType:
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            pgcode = getattr(exc.orig, "pgcode", None)
            if pgcode in INTEGRITY_ERRORS:
                raise INTEGRITY_ERRORS[pgcode] from exc
            raise
        if refresh:
            await self.session.refresh(obj)
        return obj

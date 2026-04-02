from abc import ABC
from typing import Generic, Type, TypeVar

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Base
from app.db.connections import get_session
from app.exceptions.repos import (
    NotFoundException,
    UniqueViolationException,
    NotNullViolationException,
    ForeignKeyViolationException,
)


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

    async def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        return obj

    async def create(self, obj: ModelType, refresh: bool = True) -> ModelType:
        def _create(session: AsyncSession) -> None:
            session.add(obj)

        try:
            await self.session.run_sync(_create)  # type: ignore
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            try:
                raise INTEGRITY_ERRORS[exc.orig.__dict__["pgcode"]]
            except KeyError:  # pragma: no cover
                raise exc
        if refresh:  # pragma: no cover
            await self.session.refresh(obj)
        return obj

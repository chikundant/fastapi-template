from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        from_attributes=True,
        alias_generator=to_camel,
    )

    def dump(
        self,
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_none: bool = False,
    ) -> dict:
        return self.model_dump(
            mode="json",
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_none=exclude_none,
        )

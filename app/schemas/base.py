from typing import Any
from uuid import UUID

import orjson
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


BaseConfig = ConfigDict(
    arbitrary_types_allowed=True,
    populate_by_name=True,
    from_attributes=True,
    alias_generator=to_camel,
    json_encoders={
        UUID: lambda uuid: str(uuid),
    },
)


class BaseSchema(BaseModel):
    model_config = BaseConfig

    def model_dump_json(  # type: ignore
        self,
        *,
        indent: int | None = None,
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
        return orjson.dumps(
            self.model_dump(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
            ),
            option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY,
        ).decode()

    def dump(
        self,
        include: Any = None,
        exclude: Any = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict:
        return self.model_dump(
            mode="json",
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

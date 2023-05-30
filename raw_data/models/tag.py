"""Gamedata models related to character tag information."""

import typing

import pydantic

__all__: typing.Sequence[str] = ("RawTag",)


class RawTag(pydantic.BaseModel):
    """Gamedata model containing character tag information."""

    id: int = pydantic.Field(alias="tagId")
    name: str = pydantic.Field(alias="tagName")

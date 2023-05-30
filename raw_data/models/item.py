"""Gamedata models related to Arknights item information."""

import re
import typing

import pydantic

__all__: typing.Sequence[str] = ("RawItem",)


class RawItem(pydantic.BaseModel):
    """Gamedata model containing item information."""

    id: str = pydantic.Field(alias="itemId")
    name: str
    description: str | None
    rarity: int
    icon_id: str = pydantic.Field(alias="iconId")

    @pydantic.validator("description")
    def parse_description(cls, value: str | None) -> str | None:
        """Get rid of <...> </> tags."""
        return re.sub(r"<.*?>(.*?)</>", r"**\1**", value) if value else None

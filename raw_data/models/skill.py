"""Gamedata models related to character skill information."""

import enum
import re
import typing

import pydantic

__all__: typing.Sequence[str] = ("RawSkill",)


class RegenType(enum.Enum):
    AUTO = 1
    OFFENSIVE = 2
    DEFENSIVE = 4
    DEPLOYMENT = 8


class RawSpData(pydantic.BaseModel):
    type: RegenType = pydantic.Field(alias="spType")
    cost: int = pydantic.Field(alias="spCost")
    initial: int = pydantic.Field(alias="initSp")
    charges: int = pydantic.Field(alias="maxChargeTime")


class RawSkillLevel(pydantic.BaseModel):
    name: str
    description: str
    duration: float
    sp_data: RawSpData = pydantic.Field(alias="spData")

    @pydantic.root_validator(pre=True)
    def parse_description(cls, values: dict[str, object]) -> dict[str, object]:
        description = typing.cast(str, values["description"])
        blackboard = typing.cast(list[dict[str, object]], values["blackboard"])

        # We need to go from e.g.
        # [{"id": "a", value: 1}, {"id": "b", value: 2}]
        # to
        # {"a": 1, "b": 2}
        blackboard_map: dict[str, object] = dict(map(dict.values, blackboard))  # pyright: ignore  # noqa: PGH003, E501

        # Replace colour tags by something we can actually use.
        # Sadly discord doesn't support coloured text, so we settle for bold.
        # TODO: Maybe only do this before sending so that we can actually use colour on Eludris?
        description = re.sub(r"<.*?>(.*?)</>", r"**\1**", description)

        # For some reason some format keys have a leading minus sign...
        description = re.sub(r"{(-?).*?}", "", description)

        # Ensure everything is displayed with 0 decimals.
        description = description.replace("0%", "0.0%")

        # Fill in blackboard data.
        description = description.format_map(blackboard_map)

        values["description"] = description
        return values


class RawSkill(pydantic.BaseModel):
    """Gamedata model containing character skill information."""

    id: str = pydantic.Field(alias="skillId")
    levels: typing.Sequence[RawSkillLevel]

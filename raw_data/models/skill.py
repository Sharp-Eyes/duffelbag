"""Gamedata models related to character skill information."""

import typing

import pydantic

__all__: typing.Sequence[str] = ("RawSkill", "RawSkillLevel")


def _fix_sp_type(sp_type: int | str) -> str:
    if isinstance(sp_type, int):
        assert sp_type == 8  # noqa: PLR2004
        return "ON_DEPLOYMENT"

    return sp_type


SpType = typing.Annotated[str, pydantic.BeforeValidator(_fix_sp_type)]


class RawSpData(pydantic.BaseModel):
    type: SpType = pydantic.Field(alias="spType")
    cost: int = pydantic.Field(alias="spCost")
    initial: int = pydantic.Field(alias="initSp")
    charges: int = pydantic.Field(alias="maxChargeTime")


class RawSkillBlackboard(pydantic.BaseModel):
    key: str
    value: float


class RawSkillLevel(pydantic.BaseModel):
    """Gamedata model containing character skill level information."""

    name: str
    description: str
    duration: float
    sp_data: RawSpData = pydantic.Field(alias="spData")
    blackboard: list[RawSkillBlackboard]
    skill_type: str = pydantic.Field(alias="skillType")
    duration_type: str = pydantic.Field(alias="durationType")


class RawSkill(pydantic.BaseModel):
    """Gamedata model containing character skill information."""

    id: str = pydantic.Field(alias="skillId")
    levels: typing.Sequence[RawSkillLevel]

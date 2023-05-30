"""Gamedata models related to Arknights character information."""

import typing

import pydantic

__all__: typing.Sequence[str] = ("RawCharacter",)


class RawCharacterAttributes(pydantic.BaseModel):
    HP: int = pydantic.Field(alias="maxHp")
    ATK: int = pydantic.Field(alias="atk")
    DEF: int = pydantic.Field(alias="def")
    RES: float = pydantic.Field(alias="magicResistance")
    dp_cost: int = pydantic.Field(alias="cost")
    block: int = pydantic.Field(alias="blockCnt")
    attack_speed: float = pydantic.Field(alias="baseAttackTime")
    redeploy_time: int = pydantic.Field(alias="respawnTime")
    taunt_level: int = pydantic.Field(alias="tauntLevel")


class RawAttributeKeyframe(pydantic.BaseModel):
    level: int
    data: RawCharacterAttributes


class RawItem(pydantic.BaseModel):
    id: str
    count: int


class RawPhase(pydantic.BaseModel):  # TODO: rename?
    character_id: str = pydantic.Field(alias="characterPrefabKey")
    max_level: int = pydantic.Field(alias="maxLevel")
    frames: typing.Sequence[RawAttributeKeyframe] = pydantic.Field(alias="attributesKeyFrames")
    cost: typing.Sequence[RawItem] | None = pydantic.Field(alias="evolveCost")


class RawUnlockCondition(pydantic.BaseModel):
    elite_level: int = pydantic.Field(alias="phase")
    level: int


class RawSkillCost(pydantic.BaseModel):
    unlock_condition: RawUnlockCondition = pydantic.Field("unlockCond")
    training_time: int = pydantic.Field(alias="lvlUpTime")
    cost: typing.Sequence[RawItem] | None = pydantic.Field(alias="levelUpCost")


class RawSkill(pydantic.BaseModel):
    id: str = pydantic.Field(alias="skillId")
    display_id: str | None = pydantic.Field(alias="overridePrefabKey")
    masteries: typing.Sequence[RawSkillCost] | None = pydantic.Field(alias="levelUpCostCond")


class RawTalentCandidate(pydantic.BaseModel):
    unlock_condition: RawUnlockCondition = pydantic.Field(alias="unlockCondition")
    potential: int = pydantic.Field(alias="requiredPotentialRank")
    name: str
    description: str


class RawTalent(pydantic.BaseModel):
    candidates: typing.Sequence[RawTalentCandidate]


class RawPotential(pydantic.BaseModel):  # bit of a shitty class
    type: int  # TODO: probably unnecessary.
    description: str


class RawSharedSkillCost(pydantic.BaseModel):
    unlock_condition: RawUnlockCondition = pydantic.Field("unlockCond")
    cost: typing.Sequence[RawItem] | None = pydantic.Field(alias="lvlUpCost")


class RawCharacter(pydantic.BaseModel):
    """Gamedata model containing character information."""

    name: str
    description: str
    position: str
    tags: typing.Sequence[str] = pydantic.Field(alias="tagList")
    rarity: int
    profession: str
    sub_profession: str = pydantic.Field(alias="subProfessionId")
    is_alter: bool = pydantic.Field(alias="isSpChar")

    phases: typing.Sequence[RawPhase]
    skills: typing.Sequence[RawSkill]
    talents: typing.Sequence[RawTalent]
    potentials: typing.Sequence[RawPotential] = pydantic.Field(alias="potentialRanks")
    trust_bonuses: typing.Sequence[RawAttributeKeyframe] = pydantic.Field(alias="favorKeyFrames")
    shared_skills: typing.Sequence[RawSharedSkillCost] = pydantic.Field(alias="allSkillLvlup")

    @property
    def id(self) -> str:
        """The id of the character."""
        return self.phases[0].character_id

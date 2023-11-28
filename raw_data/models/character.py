"""Gamedata models related to Arknights character information."""

import typing

import pydantic

__all__: typing.Sequence[str] = (
    "RawCharacter",
    "RawCharacterSkill",
    "RawPhase",
    "RawSkillCost",
    "RawSharedSkillCost",
)

T = typing.TypeVar("T")
Sequence = typing.Annotated[typing.Sequence[T], pydantic.AfterValidator(tuple)]


def _removeprefix_validator(prefix: str) -> pydantic.BeforeValidator:
    def _strip(target: str) -> str:
        return target.removeprefix(prefix)

    return pydantic.BeforeValidator(_strip)


PhaseValidator = _removeprefix_validator("PHASE_")
RarityValidator = _removeprefix_validator("TIER_")


class RawCharacterAttributes(pydantic.BaseModel, frozen=True):
    HP: int = pydantic.Field(alias="maxHp")
    ATK: int = pydantic.Field(alias="atk")
    DEF: int = pydantic.Field(alias="def")
    RES: float = pydantic.Field(alias="magicResistance")
    dp_cost: int = pydantic.Field(alias="cost")
    block: int = pydantic.Field(alias="blockCnt")
    attack_speed: float = pydantic.Field(alias="baseAttackTime")
    redeploy_time: int = pydantic.Field(alias="respawnTime")
    taunt_level: int = pydantic.Field(alias="tauntLevel")


class RawAttributeKeyframe(pydantic.BaseModel, frozen=True):
    level: int
    data: RawCharacterAttributes


class RawItem(pydantic.BaseModel, frozen=True):
    id: str
    count: int


class RawPhase(pydantic.BaseModel, frozen=True):  # TODO: rename?
    """Gamedata model containing character elite phase information."""

    character_id: str = pydantic.Field(alias="characterPrefabKey")
    max_level: int = pydantic.Field(alias="maxLevel")
    frames: Sequence[RawAttributeKeyframe] = pydantic.Field(alias="attributesKeyFrames")
    cost: Sequence[RawItem] | None = pydantic.Field(alias="evolveCost")


class RawUnlockCondition(pydantic.BaseModel, frozen=True):
    elite_level: typing.Annotated[int, PhaseValidator] = pydantic.Field(alias="phase")
    level: int


class RawSkillCost(pydantic.BaseModel, frozen=True):
    """Gamedata model containing character skill mastery cost information."""

    unlock_condition: RawUnlockCondition = pydantic.Field(alias="unlockCond")
    training_time: int = pydantic.Field(alias="lvlUpTime")
    cost: Sequence[RawItem] | None = pydantic.Field(alias="levelUpCost")


class RawCharacterSkill(pydantic.BaseModel, frozen=True):
    """Gamedata model containing character skill information."""

    id: str = pydantic.Field(alias="skillId")
    display_id: str | None = pydantic.Field(alias="overridePrefabKey")
    masteries: Sequence[RawSkillCost] | None = pydantic.Field(alias="levelUpCostCond")


class RawTalentCandidate(pydantic.BaseModel, frozen=True):
    unlock_condition: RawUnlockCondition = pydantic.Field(alias="unlockCondition")
    potential: int = pydantic.Field(alias="requiredPotentialRank")
    name: str
    description: str


class RawTalent(pydantic.BaseModel, frozen=True):
    candidates: Sequence[RawTalentCandidate]


class RawPotential(pydantic.BaseModel, frozen=True):  # bit of a shitty class
    type: str  # TODO: probably unnecessary.
    description: str


class RawSharedSkillCost(pydantic.BaseModel, frozen=True):
    """Gamedata model containing character shared skill cost information."""

    unlock_condition: RawUnlockCondition = pydantic.Field("unlockCond")
    cost: Sequence[RawItem] | None = pydantic.Field(alias="lvlUpCost")


class RawCharacter(pydantic.BaseModel, frozen=True):
    """Gamedata model containing character information."""

    name: str
    description: str
    position: str
    tags: Sequence[str] = pydantic.Field(alias="tagList")
    rarity: typing.Annotated[int, RarityValidator]
    profession: str
    sub_profession: str = pydantic.Field(alias="subProfessionId")
    is_alter: bool = pydantic.Field(alias="isSpChar")

    phases: Sequence[RawPhase]
    skills: Sequence[RawCharacterSkill]
    talents: Sequence[RawTalent]
    potentials: Sequence[RawPotential] = pydantic.Field(alias="potentialRanks")
    trust_bonuses: Sequence[RawAttributeKeyframe] = pydantic.Field(alias="favorKeyFrames")
    shared_skills: Sequence[RawSharedSkillCost] = pydantic.Field(alias="allSkillLvlup")

    @property
    def id(self) -> str:
        """The id of the character."""
        return self.phases[0].character_id

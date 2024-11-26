"""Module that contains logic to get and store arknights API user data."""

import decimal
import typing

import pydantic

import database
from duffelbag import shared


class HybridCharacter(pydantic.BaseModel):
    """A combination of the StaticCharacter and UserCharacter models."""

    user_character_id: int = pydantic.Field(alias="id")
    character_id: str
    user_id: int
    main_skill_lvl: int
    level: int
    exp: int
    evolve_phase: int
    name: str = pydantic.Field(alias="character_id.name")
    rarity: int = pydantic.Field(alias="character_id.rarity")
    profession: str = pydantic.Field(alias="character_id.profession")
    sub_profession: str = pydantic.Field(alias="character_id.sub_profession")


class HybridSkillLevel(pydantic.BaseModel):
    """A combination of the StaticSkill, StaticSkillLevel and StaticCharacterSkill models."""

    skill_id: str
    character_skill_id: int = pydantic.Field(alias="id")
    skill_level_id: int = pydantic.Field(alias="skill_id.id")
    character_id: str
    skill_num: int
    display_id: str
    sp_cost: int = pydantic.Field(alias="skill_id.sp_cost")
    initial_sp: int = pydantic.Field(alias="skill_id.initial_sp")
    charges: int = pydantic.Field(alias="skill_id.charges")
    duration: decimal.Decimal = pydantic.Field(alias="skill_id.duration")
    level: int = pydantic.Field(alias="skill_id.level")
    skill_type: str = pydantic.Field(alias="skill_id.skill_id.skill_type")
    sp_type: str = pydantic.Field(alias="skill_id.skill_id.sp_type")
    duration_type: str = pydantic.Field(alias="skill_id.skill_id.duration_type")


async def store_characters(arknights_user: database.ArknightsUser) -> None:
    """Fetch a user's characters and store them in the database."""
    client = await shared.ensure_user_client(arknights_user)
    data = await client.get_data()

    api_characters = data.troop.chars.values()
    parsed_characters = [
        database.UserCharacter(
            character_id=character.char_id,
            user_id=arknights_user.id,
            main_skill_lvl=character.main_skill_lvl,
            level=character.level,
            exp=character.exp,
            evolve_phase=character.evolve_phase,
        )
        for character in api_characters
    ]

    # NOTE: Inserting the characters updates the models in-place to contain the id key.
    #       We need this for foreignkeys in skills and modules.
    await (
        database.UserCharacter.insert(*parsed_characters)
        .on_conflict(
            action="DO UPDATE",
            target=(database.UserCharacter.character_id, database.UserCharacter.user_id),
            values=database.all_columns_but_pk(database.UserCharacter),
        )
    )  # fmt: skip

    skills: list[database.UserCharacterSkill] = []
    modules: list[database.UserCharacterModule] = []
    for parsed_char, character in zip(parsed_characters, api_characters, strict=True):
        skills.extend(
            database.UserCharacterSkill(
                skill_id=skill.skill_id,
                user_character_id=parsed_char.id,
                specialize_level=skill.specialize_level,
            )
            for skill in character.skills
        )

        modules.extend(
            database.UserCharacterModule(
                module_id=module_id,
                user_character_id=parsed_char.id,
                level=module.level,
            )
            for module_id, module in character.equip.items()
        )

    await (
        database.UserCharacterSkill.insert(*skills)
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.UserCharacterSkill.skill_id,
                database.UserCharacterSkill.user_character_id,
            ),
            values=database.all_columns_but_pk(database.UserCharacterSkill),
        )
    )  # fmt: skip

    await (
        database.UserCharacterModule.insert(*modules)
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.UserCharacterModule.module_id,
                database.UserCharacterModule.user_character_id,
            ),
            values=database.all_columns_but_pk(database.UserCharacterModule),
        )
    )  # fmt: skip


async def get_character(
    character_id: str,
    arknights_user: database.ArknightsUser,
) -> HybridCharacter:
    """Get a user's character data along with their static data."""
    character = await (
        database.UserCharacter.select(  # type: ignore
            *database.UserCharacter.all_columns(),
            *database.UserCharacter.character_id.all_columns(),
        )
        .where(
            (database.UserCharacter.character_id == character_id)
            & (database.UserCharacter.user_id == arknights_user.id),
        )
        .first()
    )

    assert character
    return HybridCharacter.model_validate(character)


async def get_skill_localisations(
    character: database.StaticCharacter | database.UserCharacter | HybridCharacter,
    locale: str = "en_US",
) -> typing.Sequence[database.StaticSkillLocalisation]:
    """Get localised information for a character's skills."""
    joined = (
        database.StaticSkillLocalisation.skill_id
        .join_on(database.StaticCharacterSkill.skill_id)
    )  # fmt: skip

    character_id = character.id if isinstance(character, database.StaticCharacter) else character.character_id

    return await database.StaticSkillLocalisation.objects().where(
        (joined.character_id == character_id)
        & (database.StaticSkillLocalisation.locale == locale),
    )


async def get_skill_localisation(
    skill: str | database.StaticSkill,
    character: str | database.StaticCharacter | database.UserCharacter | HybridCharacter,
    locale: str = "en_US",
) -> database.StaticSkillLocalisation:
    """Get localised information for a character's skills."""
    joined = (
        database.StaticSkillLocalisation.skill_id
        .join_on(database.StaticCharacterSkill.skill_id)
    )  # fmt: skip

    if isinstance(character, str):
        character_id = character
    elif isinstance(character, database.StaticCharacter):
        character_id = character.id
    else:
        character_id = character.character_id

    skill_id = skill if isinstance(skill, str) else skill.id

    localisation = await (
        database.StaticSkillLocalisation.objects()
        .where(
            (joined.character_id == character_id)
            & (database.StaticSkillLocalisation.locale == locale)
            & (joined.skill_id == skill_id),
        )
        .first()
    )
    assert localisation
    return localisation


async def get_skill_at_level(
    character: database.StaticCharacter | database.UserCharacter | HybridCharacter,
    skill_id: str,
    level: int,
) -> HybridSkillLevel:
    """Get aggregate skill information for a character's skill at a given level."""
    joined = database.StaticCharacterSkill.skill_id.join_on(database.StaticSkillLevel.skill_id)

    character_id = character.id if isinstance(character, database.StaticCharacter) else character.character_id

    skill = await (
        database.StaticCharacterSkill.select(  # type: ignore
            *database.StaticCharacterSkill.all_columns(),
            *joined.all_columns(exclude=["skill_id"]),
            *joined.skill_id.all_columns(),  # type: ignore
        )
        .where(
            (database.StaticCharacterSkill.skill_id == skill_id)
            & (database.StaticCharacterSkill.character_id == character_id)
            & (joined.level == level),
        )
        .first()
    )

    assert skill
    return HybridSkillLevel.model_validate(skill)


async def get_skill_level_blackboards(skill: HybridSkillLevel) -> typing.Sequence[database.StaticSkillBlackboard]:
    """Get blackboard entries for a given skill level."""
    return await (
        database.StaticSkillBlackboard.objects()
        .where(database.StaticSkillBlackboard.skill_level_id == skill.skill_level_id)
    )


TAG_LOOKUP = {
    "ba.vup": "**",
    "ba.rem": "__",
}

FMT_LOOKUP = {
    "0%": ".0%",
}

def format_skill_description(  # noqa: C901, PLR0912, PLR0915
    skill_localisation: database.StaticSkillLocalisation,
    blackboard: typing.Sequence[database.StaticSkillBlackboard],
) -> str:
    """Resolve markup tags and blackboard entries into a description string."""
    blackboard_map = {blackboard_entry.key: blackboard_entry for blackboard_entry in blackboard}

    tag_open: int | None = None
    tag_name: str | None = None
    tag_md: str | None = None

    fmt_name: str | None = None
    fmt_spec: str | None = None

    out_str = ""

    desc_iter = enumerate(skill_localisation.description)
    for i, c in desc_iter:
        if c == "<":
            i, c = next(desc_iter)  # noqa: PLW2901
            if c == "@":
                # Opening tag, check which markdown to use, then keep parsing.
                tag_open = i
                tag_name = ""
                for _, c in desc_iter:  # noqa: PLW2901
                    if c == ">":
                        break

                    tag_name += c

                tag_md = TAG_LOOKUP[tag_name]
                out_str += tag_md

            elif c == "/":
                # Closing tag, close markdown.
                if tag_open is None or tag_md is None:
                    msg = "Encountered a closing tag </> before a tag was opened."
                    raise ValueError(msg)

                _, c = next(desc_iter)  # noqa: PLW2901
                assert c == ">"

                out_str += tag_md
                tag_open = tag_name = tag_md = None

            elif tag_open is not None:
                # Closing tag found before opening tag.
                msg = f"Expected closing tag </> for tag <@{tag_name}> opened at {tag_open}, found <{c}...>"
                raise ValueError(msg)

            else:
                # Unknown tag.
                msg = f"Expected opening tag <@...>, found unexpected character {c}"
                raise ValueError(msg)

        elif c == "{":
            # Format string, collect name and spec.
            aggregator = ""
            for _, c in desc_iter:  # noqa: PLW2901
                if c == "}":
                    break
                if c == ":":
                    fmt_name = aggregator
                    aggregator = ""
                else:
                    aggregator += c

            if fmt_name is None:
                fmt_name = aggregator
                fmt_spec = ""
            else:
                fmt_spec = aggregator
            del aggregator

            # Format blackboard item.
            out_str += format(blackboard_map[fmt_name].value, FMT_LOOKUP.get(fmt_spec, fmt_spec))

            fmt_name = fmt_spec = None

        else:
            out_str += c

    return out_str

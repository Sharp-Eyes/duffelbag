"""Utility functions to populate the database with static character data."""

import typing

import database
import raw_data


async def populate_tags(
    raw_tags: typing.Sequence[raw_data.RawTag] | None = None,
    *,
    clean: bool = False,
) -> None:
    """Populate the 'tag' table in the database.

    Parameters
    ----------
    raw_tags:
        The raw tag data to process into database rows. If not provided, the
        tags will be fetched anew.
    clean:
        Whether to clear the 'tag' table before repopulating it. This could be
        used to get rid of any stale/removed tags (probably never needed).
    """
    if not raw_tags:
        raw_tags = await raw_data.fetch_tags()

    if clean:
        # Delete all existing tags...
        await database.StaticTag.delete(force=True)

    # Re-populate tags...
    await database.StaticTag.insert(
        *[database.StaticTag(name=tag.name) for tag in raw_tags],
    ).on_conflict(
        action="DO NOTHING",
    )


# TODO: Localisation.
async def populate_items(
    raw_items: typing.Sequence[raw_data.RawItem] | None = None,
    *,
    clean: bool = False,
) -> None:
    """Populate the 'item' table in the database.

    Parameters
    ----------
    raw_items:
        The raw item data to process into database rows. If not provided, the
        items will be fetched anew.
    clean:
        Whether to clear the 'item' table before repopulating it. This could be
        used to get rid of any stale/removed items (probably never needed).
    """
    if not raw_items:
        raw_items = await raw_data.fetch_items()

    if clean:
        # Delete all existing tags...
        await database.StaticItem.delete(force=True)

    # Re-populate tags...
    await database.StaticItem.insert(
        *[
            database.StaticItem(
                id=item.id,
                icon_id=item.icon_id,
                name=item.name,
                description=item.description,
                rarity=item.rarity,
            )
            for item in raw_items
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=database.StaticItem.id,
        values=database.StaticItem.all_columns(),
    )


async def populate_characters(
    raw_characters: typing.Sequence[raw_data.RawCharacter] | None = None,
    *,
    clean: bool = False,
) -> None:
    """Populate the 'character' table in the database along with all its dependencies.

    This includes the 'skill', 'character_tag', 'character_elite_phase',
    'character_elite_phase_item', 'skill_shared_upgrade', 'skill_shared_upgrade_item',
    'skill_mastery' and 'skill_mastery_item' tables.

    Parameters
    ----------
    raw_characters:
        The raw character data to process into database rows. If not provided,
        the characters will be fetched anew.
    clean:
        Whether to clear the aforementioned tables before repopulating them.
        This could be used to get rid of any stale/removed items (probably
        never needed).
        More useful is that it ensures no duplicate meta-entries are created
        while we wait for composite unique constraints to be added to piccolo.
    """
    if not raw_characters:
        raw_characters = await raw_data.fetch_characters()

    if clean:
        # This should cascade to all other tables. Thanks, foreignkeys.
        await database.StaticCharacter.delete(force=True)

    characters: list[database.StaticCharacter] = []
    tags: list[database.StaticCharacterTag] = []
    skills: dict[database.StaticCharacterSkill, raw_data.RawCharacterSkill] = {}
    elite_phases: dict[database.StaticCharacterElitePhase, raw_data.RawPhase] = {}
    shared_skill_upgrades: dict[database.StaticSkillSharedUpgrade, raw_data.RawSharedSkillCost] = {}

    for raw_character in raw_characters:
        character = database.StaticCharacter(
            id=raw_character.id,
            name=raw_character.name,
            rarity=raw_character.rarity,
            profession=raw_character.profession,
            sub_profession=raw_character.sub_profession,
            is_alter=raw_character.is_alter,
        )

        characters.append(character)

        tags.extend(
            database.StaticCharacterTag(
                character_id=character.id,
                tag_id=tag,
            )
            for tag in raw_character.tags
        )

        skills |= {
            database.StaticCharacterSkill(
                character_id=character.id,
                skill_id=skill.id,
                skill_num=num,
                display_id=skill.display_id or skill.id,
            ): skill
            for num, skill in enumerate(raw_character.skills, start=1)
        }

        # TODO: (maybe) store E0
        elite_phases |= {
            database.StaticCharacterElitePhase(
                character_id=character.id,
                level=level,
            ): elite_phase
            for level, elite_phase in enumerate(raw_character.phases[1:], start=1)
        }

        shared_skill_upgrades |= {
            database.StaticSkillSharedUpgrade(
                character_id=character.id,
                level=level,
            ): shared_skill_upgrade
            for level, shared_skill_upgrade in enumerate(raw_character.shared_skills, start=1)
        }

    await (
        database.StaticCharacter.insert(*characters)
        .on_conflict(
            action="DO UPDATE",
            target=database.StaticCharacter.id,
            values=database.all_columns_but_pk(database.StaticCharacter),
        )
    )  # fmt: skip

    await (
        database.StaticCharacterTag.insert(*tags)
        .on_conflict(
            action="DO UPDATE",
            # A given character can only have the same tag once.
            target=(database.StaticCharacterTag.character_id, database.StaticCharacterTag.tag_id),
            values=database.all_columns_but_pk(database.StaticCharacterTag),
        )
    )  # fmt: skip

    await (
        database.StaticCharacterSkill.insert(*skills.keys())
        .on_conflict(
            action="DO UPDATE",
            target=database.StaticCharacterSkill.id,
            values=database.all_columns_but_pk(database.StaticCharacterSkill),
        )
    )  # fmt: skip

    await (
        database.StaticCharacterElitePhase.insert(*elite_phases.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.StaticCharacterElitePhase.character_id,
                database.StaticCharacterElitePhase.level,
            ),
            values=database.all_columns_but_pk(database.StaticCharacterElitePhase),
        )
    )  # fmt: skip

    await (
        database.StaticSkillSharedUpgrade.insert(*shared_skill_upgrades.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.StaticSkillSharedUpgrade.character_id,
                database.StaticSkillSharedUpgrade.level,
            ),
            values=database.all_columns_but_pk(database.StaticSkillSharedUpgrade),
        )
    )  # fmt: skip

    # Parse masteries...
    skill_masteries: dict[database.StaticSkillMastery, raw_data.RawSkillCost] = {
        database.StaticSkillMastery(
            skill_id=skill.id,
            level=level,
        ): mastery
        for skill, raw_skill in skills.items()
        if raw_skill.masteries
        for level, mastery in enumerate(raw_skill.masteries, start=1)
    }

    await (
        database.StaticSkillMastery.insert(*skill_masteries.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.StaticSkillMastery.skill_id,
                database.StaticSkillMastery.level,
            ),
            values=database.all_columns_but_pk(database.StaticSkillMastery),
        )
    )  # fmt: skip

    # Parse mastery costs...
    await database.StaticSkillMasteryItem.insert(
        *[
            database.StaticSkillMasteryItem(
                mastery_id=mastery.id,
                item_id=item.id,
                quantity=item.count,
            )
            for mastery, raw_mastery in skill_masteries.items()
            if raw_mastery.cost
            for item in raw_mastery.cost
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=(
            database.StaticSkillMasteryItem.mastery_id,
            database.StaticSkillMasteryItem.item_id,
        ),
        values=database.all_columns_but_pk(database.StaticSkillMasteryItem),
    )

    # Parse elite level costs...
    await database.StaticCharacterElitePhaseItem.insert(
        *[
            database.StaticCharacterElitePhaseItem(
                elite_phase_id=elite_phase.id,
                item_id=item.id,
                quantity=item.count,
            )
            for elite_phase, raw_elite_phase in elite_phases.items()
            if raw_elite_phase.cost
            for item in raw_elite_phase.cost
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=(
            database.StaticCharacterElitePhaseItem.elite_phase_id,
            database.StaticCharacterElitePhaseItem.item_id,
        ),
        values=database.all_columns_but_pk(database.StaticCharacterElitePhaseItem),
    )

    # Parse shared skill upgrades...
    await database.StaticSkillSharedUpgradeItem.insert(
        *[
            database.StaticSkillSharedUpgradeItem(
                skill_upgrade_id=shared_skill_upgrade.id,
                item_id=item.id,
                quantity=item.count,
            )
            for shared_skill_upgrade, raw_shared_skill_upgrade in shared_skill_upgrades.items()
            if raw_shared_skill_upgrade.cost
            for item in raw_shared_skill_upgrade.cost
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=(
            # A given elite phase can only contain the same item type once.
            database.StaticSkillSharedUpgradeItem.skill_upgrade_id,
            database.StaticSkillSharedUpgradeItem.item_id,
        ),
        values=database.all_columns_but_pk(database.StaticSkillSharedUpgradeItem),
    )


async def populate_skills(
    raw_skills: typing.Sequence[raw_data.RawSkill] | None = None,
    *,
    locale: str = "en_US",
    clean: bool = False,
) -> None:
    """Populate the 'static_skill' table in the database along with all its dependencies.

    Parameters
    ----------
    raw_skills:
        The raw skill data to process into database rows. If not provided,
        the skills will be fetched anew.
    locale:
        The locale for which to store skill information.
    clean:
        Whether to clear the aforementioned tables before repopulating them.
        This could be used to get rid of any stale/removed items (probably
        never needed).
        More useful is that it ensures no duplicate meta-entries are created
        while we wait for composite unique constraints to be added to piccolo.
    """
    if not raw_skills:
        raw_skills = await raw_data.fetch_skills()

    if clean:
        await database.StaticSkill.delete(force=True)

    skills = [
        database.StaticSkill(
            id=skill.id,
            skill_type=skill.levels[0].skill_type,
            duration_type=skill.levels[0].duration_type,
            sp_type=skill.levels[0].sp_data.type,
        )
        for skill in raw_skills
    ]
    await database.StaticSkill.insert(*skills)

    skill_levels: dict[database.StaticSkillLevel, raw_data.RawSkillLevel] = {}
    skill_localisations: list[database.StaticSkillLocalisation] = []

    for skill, raw_skill in zip(skills, raw_skills, strict=True):
        skill_levels |= {
            database.StaticSkillLevel(
                skill_id=skill.id,
                sp_cost=level.sp_data.cost,
                initial_sp=level.sp_data.initial,
                charges=level.sp_data.charges,
                duration=level.duration,
            ): level
            for level in raw_skill.levels
        }

        skill_localisations.append(
            database.StaticSkillLocalisation(
                skill_id=skill.id,
                locale=locale,
                name=raw_skill.levels[0].name,
                description=raw_skill.levels[0].description,
            ),
        )

    await database.StaticSkillLevel.insert(*skill_levels.keys())
    await database.StaticSkillLocalisation.insert(*skill_localisations)

    skill_blackboards: list[database.StaticSkillBlackboard] = []

    for skill_level, raw_skill_level in skill_levels.items():
        skill_blackboards.extend(
            database.StaticSkillBlackboard(
                skill_level_id=skill_level.id,
                key=blackboard_entry.key,
                value=blackboard_entry.value,
            )
            for blackboard_entry in raw_skill_level.blackboard
        )

    await database.bulk_insert(*skill_blackboards)

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
        await database.Tag.delete(force=True)

    # Re-populate tags...
    await database.Tag.insert(
        *[database.Tag(name=tag.name) for tag in raw_tags],
    ).on_conflict(
        action="DO NOTHING",
    )


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
        await database.Item.delete(force=True)

    # Re-populate tags...
    await database.Item.insert(
        *[
            database.Item(
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
        target=database.Item.id,
        values=database.Item.all_columns(),
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
        await database.Character.delete(force=True)

    characters: list[database.Character] = []
    tags: list[database.CharacterTag] = []
    skills: dict[database.Skill, raw_data.RawCharacterSkill] = {}
    elite_phases: dict[database.CharacterElitePhase, raw_data.RawPhase] = {}
    shared_skill_upgrades: dict[database.SkillSharedUpgrade, raw_data.RawSharedSkillCost] = {}

    for raw_character in raw_characters:
        character = database.Character(
            id=raw_character.id,
            name=raw_character.name,
            rarity=raw_character.rarity,
            profession=raw_character.profession,
            sub_profession=raw_character.sub_profession,
            is_alter=raw_character.is_alter,
        )

        characters.append(character)

        tags.extend(
            database.CharacterTag(
                character=character.id,
                tag=tag,
            )
            for tag in raw_character.tags
        )

        skills |= {
            database.Skill(
                character_id=character.id,
                skill_id=skill.id,
                display_id=skill.display_id,
            ): skill
            for skill in raw_character.skills
        }

        # TODO: (maybe) store E0
        elite_phases |= {
            database.CharacterElitePhase(
                character=character.id,
                level=level,
            ): elite_phase
            for level, elite_phase in enumerate(raw_character.phases[1:], start=1)
        }

        shared_skill_upgrades |= {
            database.SkillSharedUpgrade(
                character=character.id,
                level=level,
            ): shared_skill_upgrade
            for level, shared_skill_upgrade in enumerate(raw_character.shared_skills, start=1)
        }

    await (
        database.Character.insert(*characters)
        .on_conflict(
            action="DO UPDATE",
            target=database.Character.id,
            values=database.all_columns_but_pk(database.Character),
        )
    )  # fmt: skip

    await (
        database.CharacterTag.insert(*tags)
        .on_conflict(
            action="DO UPDATE",
            # A given character can only have the same tag once.
            target=(database.CharacterTag.character, database.CharacterTag.tag),
            values=database.all_columns_but_pk(database.CharacterTag),
        )
    )  # fmt: skip

    await (
        database.Skill.insert(*skills.keys())
        .on_conflict(
            action="DO UPDATE",
            target=database.Skill.id,
            values=database.all_columns_but_pk(database.Skill),
        )
    )  # fmt: skip

    await (
        database.CharacterElitePhase.insert(*elite_phases.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.CharacterElitePhase.character,
                database.CharacterElitePhase.level,
            ),
            values=database.all_columns_but_pk(database.CharacterElitePhase),
        )
    )  # fmt: skip

    await (
        database.SkillSharedUpgrade.insert(*shared_skill_upgrades.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.SkillSharedUpgrade.character,
                database.SkillSharedUpgrade.level,
            ),
            values=database.all_columns_but_pk(database.SkillSharedUpgrade),
        )
    )  # fmt: skip

    # Parse masteries...
    skill_masteries: dict[database.SkillMastery, raw_data.RawSkillCost] = {
        database.SkillMastery(
            skill=skill.id,
            level=level,
        ): mastery
        for skill, raw_skill in skills.items()
        if raw_skill.masteries
        for level, mastery in enumerate(raw_skill.masteries, start=1)
    }

    await (
        database.SkillMastery.insert(*skill_masteries.keys())
        .on_conflict(
            action="DO UPDATE",
            target=(
                database.SkillMastery.skill,
                database.SkillMastery.level,
            ),
            values=database.all_columns_but_pk(database.SkillMastery),
        )
    )  # fmt: skip

    # Parse mastery costs...
    await database.SkillMasteryItem.insert(
        *[
            database.SkillMasteryItem(
                mastery=mastery.id,
                item=item.id,
                quantity=item.count,
            )
            for mastery, raw_mastery in skill_masteries.items()
            if raw_mastery.cost
            for item in raw_mastery.cost
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=(
            database.SkillMasteryItem.mastery,
            database.SkillMasteryItem.item,
        ),
        values=database.all_columns_but_pk(database.SkillMasteryItem),
    )

    # Parse elite level costs...
    await database.CharacterElitePhaseItem.insert(
        *[
            database.CharacterElitePhaseItem(
                elite_phase=elite_phase.id,
                item=item.id,
                quantity=item.count,
            )
            for elite_phase, raw_elite_phase in elite_phases.items()
            if raw_elite_phase.cost
            for item in raw_elite_phase.cost
        ],
    ).on_conflict(
        action="DO UPDATE",
        target=(
            # A given elite phase can only contain the same item type once.
            database.CharacterElitePhaseItem.elite_phase,
            database.CharacterElitePhaseItem.item,
        ),
        values=database.all_columns_but_pk(database.CharacterElitePhaseItem),
    )

    # Parse shared skill upgrades...
    await database.SkillSharedUpgradeItem.insert(
        *[
            database.SkillSharedUpgradeItem(
                upgrade=shared_skill_upgrade.id,
                item=item.id,
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
            database.SkillSharedUpgradeItem.upgrade,
            database.SkillSharedUpgradeItem.item,
        ),
        values=database.all_columns_but_pk(database.SkillSharedUpgradeItem),
    )

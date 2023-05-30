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
        ]
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
    # TODO: Uncomment `on_conflict` blocks when composite unique constraints
    #       are added to piccolo.

    if not raw_characters:
        raw_characters = await raw_data.fetch_characters()

    if clean:
        # This should cascade to all other tables. Thanks, foreignkeys.
        await database.Character.delete(force=True)

    db = database.get_db_from_table(database.Character)

    for character in raw_characters:
        async with db.transaction():
            # Insert character.
            await database.Character.insert(
                database.Character(
                    id=character.id,
                    name=character.name,
                    rarity=character.rarity,
                    profession=character.profession,
                    sub_profession=character.sub_profession,
                    is_alter=character.is_alter,
                )
            ).on_conflict(
                action="DO UPDATE",
                target=database.Character.id,
                values=database.Character.all_columns(),
            )

            # Insert tags.
            for tag in character.tags:
                await database.CharacterTag.insert(
                    database.CharacterTag(
                        character=character.id,
                        tag=tag,
                    )
                )
                # .on_conflict(
                #     action="DO UPDATE",
                #     # A given character can only have the same tag once.
                #     target=(database.CharacterTag.character, database.CharacterTag.tag),
                #     values=database.CharacterTag.all_columns()
                # )

            # Insert skills.
            for skill in character.skills:
                # Skill row...
                await database.Skill.insert(
                    database.Skill(
                        id=skill.id,
                        display_id=skill.display_id,
                    )
                ).on_conflict(
                    action="DO UPDATE",
                    target=database.Skill.id,
                    values=database.Skill.all_columns(),
                )

                # Skill mastery...
                if not skill.masteries:
                    continue

                for level, mastery in enumerate(skill.masteries, start=1):
                    mastery_result = await database.SkillMastery.insert(
                        database.SkillMastery(
                            character=character.id,
                            skill=skill.id,
                            level=level,
                        )
                    )
                    # .on_conflict(
                    #     action="DO UPDATE",
                    #     target=(
                    #         database.SkillMastery.character,
                    #         database.SkillMastery.skill,
                    #         database.SkillMastery.level,
                    #     ),
                    #     values=database.SkillMastery.all_columns()
                    # )

                    mastery_id: int = mastery_result[0]["id"]

                    # If the mastery exists, it should have a cost.
                    if not mastery.cost:
                        continue

                    for item in mastery.cost:
                        await database.SkillMasteryItem.insert(
                            database.SkillMasteryItem(
                                mastery=mastery_id,
                                item=item.id,
                                quantity=item.count,
                            )
                        )
                        # .on_conflict(
                        #     action="DO UPDATE",
                        #     target=(
                        #         # A given mastery can only contain the same item type once.
                        #         database.SkillMasteryItem.mastery,
                        #         database.SkillMasteryItem.item,
                        #     ),
                        #     values=[database.SkillMasteryItem.quantity]
                        # )

            # Insert elite levels.
            # TODO: Store stats, store elite 0.
            for level, elite_phase in enumerate(character.phases[1:], start=1):
                # Elite phase row...
                elite_phase_result = await database.CharacterElitePhase.insert(
                    database.CharacterElitePhase(
                        character=character.id,
                        level=level,
                    )
                )
                # .on_conflict(
                #     action="DO UPDATE",
                #     target=(
                #         database.CharacterElitePhase.character,
                #         database.CharacterElitePhase.level,
                #     ),
                #     values=database.CharacterElitePhase.all_columns()
                # )

                elite_phase_id: int = elite_phase_result[0]["id"]

                # If the elite phase exists, it should have a cost.
                if not elite_phase.cost:
                    continue

                for item in elite_phase.cost:
                    await database.CharacterElitePhaseItem.insert(
                        database.CharacterElitePhaseItem(
                            elite_phase=elite_phase_id,
                            item=item.id,
                            quantity=item.count,
                        )
                    )
                    # .on_conflict(
                    #     action="DO UPDATE",
                    #     target=(
                    #         # A given elite phase can only contain the same item type once.
                    #         database.CharacterElitePhaseItem.elite_phase,
                    #         database.CharacterElitePhaseItem.item,
                    #     ),
                    #     values=[database.CharacterElitePhaseItem.quantity]
                    # )

            # Insert shared skill costs.
            for level, shared_skill_upgrade in enumerate(character.shared_skills, start=1):
                skill_cost_result = await database.SkillSharedUpgrade.insert(
                    database.SkillSharedUpgrade(
                        character=character.id,
                        level=level,
                    )
                )
                # .on_conflict(
                #     action="DO UPDATE",
                #     target=(
                #         database.SkillSharedUpgrade.character,
                #         database.SkillSharedUpgrade.level,
                #     ),
                #     values=database.SkillSharedUpgrade.all_columns()
                # )

                skill_cost_id: int = skill_cost_result[0]["id"]

                # If the skill level exists, it should have a cost.
                if not shared_skill_upgrade.cost:
                    continue

                for item in shared_skill_upgrade.cost:
                    await database.SkillSharedUpgradeItem.insert(
                        database.SkillSharedUpgradeItem(
                            upgrade=skill_cost_id,
                            item=item.id,
                            quantity=item.count,
                        )
                    )
                    # .on_conflict(
                    #     action="DO UPDATE",
                    #     target=(
                    #         # A given elite phase can only contain the same item type once.
                    #         database.SkillSharedUpgradeItem.upgrade,
                    #         database.SkillSharedUpgradeItem.item,
                    #     ),
                    #     values=[database.SkillSharedUpgradeItem.quantity]
                    # )

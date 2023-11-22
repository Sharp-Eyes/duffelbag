"""Module that contains logic to get and store arknights API user data."""

import database
from duffelbag import shared


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
            target=(
                database.UserCharacter.character_id,
                database.UserCharacter.user_id,
            ),
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

from piccolo import table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-11-23T20:29:04:360182"
VERSION = "1.1.1"
DESCRIPTION = "Add composite unique constraints to static models"


# This is just a dummy table we use to execute raw SQL with:
class RawTable(table.Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    async def run():
        # Add composite unique constraint to UserCharacter:
        await RawTable.raw(
            "ALTER TABLE user_character"
            " ADD CONSTRAINT user_character_character_id_user_id_key"
            " UNIQUE (character_id, user_id);"
        )

        # Add composite unique constraint to UserCharacterSkill:
        await RawTable.raw(
            "ALTER TABLE user_character_skill"
            " ADD CONSTRAINT user_character_skill_skill_id_user_character_id_key"
            " UNIQUE (skill_id, user_character_id);"
        )

        # Add composite unique constraint to UserCharacterModule:
        await RawTable.raw(
            "ALTER TABLE user_character_module"
            " ADD CONSTRAINT user_character_module_module_id_user_character_id_key"
            " UNIQUE (module_id, user_character_id);"
        )

    manager.add_raw(run)  # type: ignore

    async def run_backwards():
        # Remove composite unique constraint from UserCharacterSkill:
        await RawTable.raw(
            "ALTER TABLE user_character"
            " DROP CONSTRAINT user_character_character_id_user_id_key;"
        )

        # Remove composite unique constraint from UserCharacterSkill:
        await RawTable.raw(
            "ALTER TABLE user_character_skill"
            " DROP CONSTRAINT user_character_skill_skill_id_user_character_id_key;"
        )

        # Remove composite unique constraint from UserCharacterModule:
        await RawTable.raw(
            "ALTER TABLE user_character_module"
            " DROP CONSTRAINT user_character_module_module_id_user_character_id_key;"
        )

    manager.add_raw_backwards(run_backwards)  # type: ignore

    return manager


from piccolo import table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-11-23T20:35:19:406775"
VERSION = "1.1.1"
DESCRIPTION = "Add composite unique constraints to static models."


# This is just a dummy table we use to execute raw SQL with:
class RawTable(table.Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    async def run():
        # Add composite unique constraint to StaticCharacterTag:
        await RawTable.raw(
            "ALTER TABLE static_character_tag"
            " ADD CONSTRAINT static_character_tag_character_id_tag_id_key"
            " UNIQUE (character_id, tag_id);"
        )

        # Add composite unique constraint to StaticCharacterElitePhase:
        await RawTable.raw(
            "ALTER TABLE static_character_elite_phase"
            " ADD CONSTRAINT static_character_elite_phase_character_id_level_key"
            " UNIQUE (character_id, level);"
        )

        # Add composite unique constraint to StaticCharacterElitePhaseItem:
        await RawTable.raw(
            "ALTER TABLE static_character_elite_phase_item"
            " ADD CONSTRAINT static_character_elite_phase_item_elite_phase_id_item_id_key"
            " UNIQUE (elite_phase_id, item_id);"
        )

        # Add composite unique constraint to StaticSharedSkillUpgrade:
        await RawTable.raw(
            "ALTER TABLE static_skill_shared_upgrade"
            " ADD CONSTRAINT static_skill_shared_upgrade_character_id_level_key"
            " UNIQUE (character_id, level);"
        )
        # Add composite unique constraint to StaticSkillSharedUpgradeItem:
        await RawTable.raw(
            "ALTER TABLE static_skill_shared_upgrade_item"
            " ADD CONSTRAINT static_skill_shared_upgrade_item_skill_upgrade_id_item_id_key"
            " UNIQUE (skill_upgrade_id, item_id);"
        )

        # Add composite unique constraint to StaticSkillMastery:
        await RawTable.raw(
            "ALTER TABLE static_skill_mastery"
            " ADD CONSTRAINT static_skill_mastery_skill_id_level_key"
            " UNIQUE (skill_id, level);"
        )

        # Add composite unique constraint to StaticSkillMasteryItem:
        await RawTable.raw(
            "ALTER TABLE static_skill_mastery_item"
            " ADD CONSTRAINT static_skill_mastery_item_mastery_id_item_id_key"
            " UNIQUE (mastery_id, item_id);"
        )


    manager.add_raw(run)  # type: ignore

    async def run_backwards():
        # Remove composite unique constraint from StaticCharacterTag:
        await RawTable.raw(
            "ALTER TABLE static_character_tag"
            " DROP CONSTRAINT static_character_tag_character_id_tag_id_key;"
        )

        # Remove composite unique constraint from StaticCharacterElitePhase:
        await RawTable.raw(
            "ALTER TABLE static_character_elite_phase"
            " DROP CONSTRAINT static_character_elite_phase_character_id_level_key;"
        )

        # Remove composite unique constraint from StaticCharacterElitePhaseItem:
        await RawTable.raw(
            "ALTER TABLE static_character_elite_phase_item"
            " DROP CONSTRAINT static_character_elite_phase_item_elite_phase_id_item_id_key;"
        )

        # Remove composite unique constraint from StaticSharedSkillUpgrade:
        await RawTable.raw(
            "ALTER TABLE static_skill_shared_upgrade"
            " DROP CONSTRAINT static_skill_shared_upgrade_character_id_level_key;"
        )
        # Remove composite unique constraint from StaticSkillSharedUpgradeItem:
        await RawTable.raw(
            "ALTER TABLE static_skill_shared_upgrade_item"
            " DROP CONSTRAINT static_skill_shared_upgrade_item_skill_upgrade_id_item_id_key;"
        )

        # Remove composite unique constraint from StaticSkillMastery:
        await RawTable.raw(
            "ALTER TABLE static_skill_mastery"
            " DROP CONSTRAINT static_skill_mastery_skill_id_level_key;"
        )

        # Remove composite unique constraint from StaticSkillMasteryItem:
        await RawTable.raw(
            "ALTER TABLE static_skill_mastery_item"
            " DROP CONSTRAINT static_skill_mastery_item_mastery_id_item_id_key;"
        )

    manager.add_raw_backwards(run_backwards)  # type: ignore

    return manager

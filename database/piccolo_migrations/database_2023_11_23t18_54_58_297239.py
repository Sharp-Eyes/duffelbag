from piccolo import table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-11-23T18:54:58:297239"
VERSION = "1.1.1"
DESCRIPTION = ""


# This is just a dummy table we use to execute raw SQL with:
class RawTable(table.Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    async def run():
        # Add composite unique constraint to CharacterTag:
        await RawTable.raw(
            "ALTER TABLE character_tag"
            " ADD CONSTRAINT character_tag_character_tag_key"
            " UNIQUE (character, tag);"
        )

        # Add composite unique constraint to CharacterElitePhase:
        await RawTable.raw(
            "ALTER TABLE character_elite_phase"
            " ADD CONSTRAINT character_elite_phase_character_level_key"
            " UNIQUE (character, level);"
        )

        # Add composite unique constraint to SharedSkillUpgrade:
        await RawTable.raw(
            "ALTER TABLE skill_shared_upgrade"
            " ADD CONSTRAINT skill_shared_upgrade_character_level_key"
            " UNIQUE (character, level);"
        )

        # Add composite unique constraint to SkillMastery:
        await RawTable.raw(
            "ALTER TABLE skill_mastery"
            " ADD CONSTRAINT skill_mastery_skill_level_key"
            " UNIQUE (skill, level);"
        )

        # Add composite unique constraint to SkillMasteryItem:
        await RawTable.raw(
            "ALTER TABLE skill_mastery_item"
            " ADD CONSTRAINT skill_mastery_item_mastery_item_key"
            " UNIQUE (mastery, item);"
        )

        # Add composite unique constraint to CharacterElitePhaseItem:
        await RawTable.raw(
            "ALTER TABLE character_elite_phase_item"
            " ADD CONSTRAINT character_elite_phase_item_elite_phase_item_key"
            " UNIQUE (elite_phase, item);"
        )

        # Add composite unique constraint to SkillSharedUpgradeItem:
        await RawTable.raw(
            "ALTER TABLE skill_shared_upgrade_item"
            " ADD CONSTRAINT skill_shared_upgrade_item_upgrade_item_key"
            " UNIQUE (upgrade, item);"
        )

    manager.add_raw(run)

    async def run_backwards():
        # Remove composite unique constraint from CharacterTag:
        await RawTable.raw(
            "ALTER TABLE character_tag"
            " DROP CONSTRAINT character_tag_character_tag_key;"
        )

        # Remove composite unique constraint from CharacterElitePhase:
        await RawTable.raw(
            "ALTER TABLE character_elite_phase"
            " DROP CONSTRAINT character_elite_phase_character_level_key;"
        )

        # Remove composite unique constraint from SharedSkillUpgrade:
        await RawTable.raw(
            "ALTER TABLE skill_shared_upgrade"
            " DROP CONSTRAINT skill_shared_upgrade_character_level_key;"
        )

        # Remove composite unique constraint from SkillMastery:
        await RawTable.raw(
            "ALTER TABLE skill_mastery"
            " DROP CONSTRAINT skill_mastery_skill_level_key;"
        )

        # Remove composite unique constraint from SkillMasteryItem:
        await RawTable.raw(
            "ALTER TABLE skill_mastery_item"
            " DROP CONSTRAINT skill_mastery_item_mastery_item_key;"
        )

        # Remove composite unique constraint from CharacterElitePhaseItem:
        await RawTable.raw(
            "ALTER TABLE character_elite_phase_item"
            " DROP CONSTRAINT character_elite_phase_item_elite_phase_item_key;"
        )

        # Remove composite unique constraint from SkillSharedUpgradeItem:
        await RawTable.raw(
            "ALTER TABLE skill_shared_upgrade_item"
            " DROP CONSTRAINT skill_shared_upgrade_item_upgrade_item_key;"
        )

    manager.add_raw_backwards(run_backwards)

    return manager

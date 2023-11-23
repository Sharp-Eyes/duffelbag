from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-11-23T16:29:36:912882"
VERSION = "1.1.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.drop_table(
        class_name="SkillMasteryItem", tablename="skill_mastery_item", schema=None
    )

    manager.drop_table(
        class_name="SkillMastery", tablename="skill_mastery", schema=None
    )

    manager.drop_table(class_name="Skill", tablename="skill", schema=None)

    return manager

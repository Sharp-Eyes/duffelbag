from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Decimal


ID = "2024-11-26T11:21:14:334996"
VERSION = "1.22.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="StaticSkillBlackboard",
        tablename="static_skill_blackboard",
        column_name="value",
        db_column_name="value",
        params={"digits": (12, 4)},
        old_params={"digits": (8, 4)},
        column_class=Decimal,
        old_column_class=Decimal,
        schema=None,
    )

    return manager

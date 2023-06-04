from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Email


ID = "2023-06-04T23:38:53:562274"
VERSION = "0.113.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="email",
        db_column_name="email",
        params={"null": False},
        old_params={"null": True},
        column_class=Email,
        old_column_class=Email,
    )

    return manager

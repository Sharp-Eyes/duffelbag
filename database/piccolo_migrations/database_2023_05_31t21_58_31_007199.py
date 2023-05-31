from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar


ID = "2023-05-31T21:58:31:007199"
VERSION = "0.113.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="password",
        db_column_name="password",
        params={"length": 97},
        old_params={"length": 32},
        column_class=Varchar,
        old_column_class=Varchar,
    )

    return manager

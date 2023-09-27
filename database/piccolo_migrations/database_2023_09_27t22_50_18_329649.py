from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-09-27T22:50:18:329649"
VERSION = "1.0a2"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.rename_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        old_column_name="email",
        new_column_name="game_uid",
        old_db_column_name="email",
        new_db_column_name="game_uid",
        schema=None,
    )

    return manager

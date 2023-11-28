from piccolo import table
from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2023-11-28T00:47:23:339486"
VERSION = "1.1.1"
DESCRIPTION = "Add composite unique constraints to auth models"


# This is just a dummy table we use to execute raw SQL with:
class RawTable(table.Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )


    async def run():
        # Add composite unique constraint to PlatformUser:
        RawTable.raw(
            "ALTER TABLE platform_user"
            " ADD CONSTRAINT platform_user_platform_id_platform_name_key"
            " UNIQUE (platform_id, platform_name);"
        )

        # Add composite unique constraint to ArknightsUser:
        RawTable.raw(
            "ALTER TABLE arknights_user"
            " ADD CONSTRAINT arknights_user_channel_uid_yostar_token_key"
            " UNIQUE (channel_uid, yostar_token);"
        )

    manager.add_raw(run)  # type: ignore

    async def run_backwards():
        # Remove composite unique constraint from PlatformUser:
        RawTable.raw(
            "ALTER TABLE platform_user"
            " DROP CONSTRAINT platform_user_platform_id_platform_name_key;"
        )

        # Remove composite unique constraint from ArknightsUser:
        RawTable.raw(
            "ALTER TABLE arknights_user"
            " DROP CONSTRAINT arknights_user_channel_uid_yostar_token_key;"
        )


    manager.add_raw_backwards(run_backwards)  # type: ignore

    return manager

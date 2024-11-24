from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import SmallInt
from piccolo.columns.indexes import IndexMethod


ID = "2023-11-29T00:47:33:546439"
VERSION = "1.1.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="level",
        db_column_name="level",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager

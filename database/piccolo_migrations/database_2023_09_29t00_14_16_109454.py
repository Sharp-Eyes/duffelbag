from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Email
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class ArknightsUser(Table, tablename="arknights_user", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class DuffelbagUser(Table, tablename="duffelbag_user", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


ID = "2023-09-29T00:14:16:109454"
VERSION = "1.0a2"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="user",
        db_column_name="user",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
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

    manager.add_column(
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="arknights_user",
        db_column_name="arknights_user",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": ArknightsUser,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="deletion_ts",
        db_column_name="deletion_ts",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
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

    manager.alter_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="game_uid",
        db_column_name="game_uid",
        params={"length": 8},
        old_params={"length": 255},
        column_class=Varchar,
        old_column_class=Email,
        schema=None,
    )

    return manager

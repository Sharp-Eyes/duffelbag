from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import BigInt
from piccolo.columns.column_types import Boolean
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


ID = "2023-11-28T00:45:47:285429"
VERSION = "1.1.1"
DESCRIPTION = "Add auth models"


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="ArknightsUser",
        tablename="arknights_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="DuffelbagUser",
        tablename="duffelbag_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="PlatformUser",
        tablename="platform_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
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
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="channel_uid",
        db_column_name="channel_uid",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 16,
            "default": "",
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

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="yostar_token",
        db_column_name="yostar_token",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
            "default": "",
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

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="server",
        db_column_name="server",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 4,
            "default": "",
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

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="active",
        db_column_name="active",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
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

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="game_uid",
        db_column_name="game_uid",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 8,
            "default": "",
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

    manager.add_column(
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="username",
        db_column_name="username",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
            "default": "",
            "null": False,
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
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="password",
        db_column_name="password",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 97,
            "default": "",
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

    manager.add_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
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
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="platform_id",
        db_column_name="platform_id",
        column_class_name="BigInt",
        column_class=BigInt,
        params={
            "default": 0,
            "null": True,
            "primary_key": False,
            "unique": True,
            "index": True,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="platform_name",
        db_column_name="platform_name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 16,
            "default": "",
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

    manager.add_column(
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
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
        column_name="arknights_id",
        db_column_name="arknights_id",
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

    manager.add_column(
        table_class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
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
        table_class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
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

    return manager

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import BigInt
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


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


class UserIdentity(Table, tablename="user_identity", schema=None):
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


ID = "2023-05-30T16:05:11:044470"
VERSION = "0.112.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="DuffelbagUser",
        tablename="duffelbag_user",
        schema=None,
        columns=None,
    )

    manager.rename_table(
        old_class_name="UserIdentity",
        old_tablename="user_identity",
        new_class_name="PlatformUser",
        new_tablename="platform_user",
    )

    manager.drop_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="discord_id",
        db_column_name="discord_id",
    )

    manager.drop_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="eludris_id",
        db_column_name="eludris_id",
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
    )

    manager.add_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
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
    )

    manager.alter_column(
        table_class_name="Auth",
        tablename="auth",
        column_name="user",
        db_column_name="user",
        params={"references": DuffelbagUser},
        old_params={"references": UserIdentity},
        column_class=ForeignKey,
        old_column_class=ForeignKey,
    )

    return manager

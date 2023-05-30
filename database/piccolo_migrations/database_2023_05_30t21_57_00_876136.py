from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Email
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2023-05-30T21:57:00:876136"
VERSION = "0.113.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.rename_table(
        old_class_name="Auth",
        old_tablename="auth",
        new_class_name="ArknightsUser",
        new_tablename="arknights_user",
    )

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="email",
        db_column_name="email",
        column_class_name="Email",
        column_class=Email,
        params={
            "length": 255,
            "default": "",
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

    manager.add_column(
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="password",
        db_column_name="password",
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
    )

    return manager

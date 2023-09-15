"""The piccolo application that interfaces with the underlying PostgreSQL database."""

import pathlib

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()

APP_CONFIG = AppConfig(
    app_name="database",
    migrations_folder_path=str(CURRENT_DIRECTORY / "piccolo_migrations"),
    table_classes=table_finder(modules=["database.models"], exclude_imported=False),
    migration_dependencies=[],
    commands=[],
)

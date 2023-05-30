"""The piccolo application that interfaces with the underlying PostgreSQL database."""

import os

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="database",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=table_finder(modules=["database.models"], exclude_imported=False),
    migration_dependencies=[],
    commands=[],
)

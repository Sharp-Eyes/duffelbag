# pyright: reportPrivateUsage = false

"""Simple database utilities."""

import typing

from piccolo import engine, table


def get_db_from_table(table_: type[table.Table]) -> engine.PostgresEngine:
    """Get the database from any piccolo table."""
    return typing.cast(
        engine.PostgresEngine, table_._meta.db  # pyright: ignore[reportUnknownMemberType]
    )

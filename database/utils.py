# pyright: reportPrivateUsage = false

"""Simple database utilities."""

import typing

from piccolo import columns, engine, table

__all__: typing.Sequence[str] = (
    "all_columns_but_pk",
    "get_db",
    "rollback_transaction",
)


class _MetaTable(table.Table):
    # NOTE: This meta table only serves to access piccolo database features.
    ...


def get_db() -> engine.PostgresEngine:
    """Get the database from any piccolo table."""
    return typing.cast(
        engine.PostgresEngine,
        _MetaTable._meta.db,  # pyright: ignore  # noqa: SLF001
    )


async def rollback_transaction() -> None:
    """Rollback the currently active transaction, if any."""
    transaction = get_db().current_transaction.get()
    if transaction:
        await transaction.rollback()


def all_columns_but_pk(table_: type[table.Table], /) -> list[columns.Column]:
    """Get all columns of a table except for the primary key column.

    Useful in ON CONFLICT DO UPDATE statements to preserve auto-increment pk numbers.
    """
    return [
        col
        for col in table_._meta.columns  # noqa: SLF001
        if col is not table_._meta.primary_key  # noqa: SLF001
    ]

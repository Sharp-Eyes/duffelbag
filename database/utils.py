# pyright: reportPrivateUsage = false

"""Simple database utilities."""

import typing

from piccolo import engine, table

__all__: typing.Sequence[str] = ("get_db", "rollback_transaction")


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

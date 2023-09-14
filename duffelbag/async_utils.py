"""Utilities for asyncio patterns."""

import asyncio
import contextlib
import typing

_tasks: set[asyncio.Task[typing.Any]] = set()


def safe_task(
    coroutine: typing.Coroutine[typing.Any, typing.Any, typing.Any]
) -> asyncio.Task[typing.Any]:
    """Create an asyncio background task without risk of it being GC'd."""
    task = asyncio.create_task(coroutine)

    _tasks.add(task)
    task.add_done_callback(_tasks.discard)

    return task


async def cancel_futures(futures: typing.Iterable[asyncio.Future[typing.Any]]) -> None:
    """Ensure all provided futures are cancelled."""
    for future in futures:
        if not future.done() and not future.cancelled():
            future.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await future


async def first_completed(
    *awaitables: typing.Awaitable[typing.Any],
    timeout: float | None = None,
) -> object:
    """Return the result of the first provided awaitable, cancel the rest."""
    futures = tuple(map(asyncio.ensure_future, awaitables))
    iter_ = asyncio.as_completed(futures, timeout=timeout)

    try:
        return await next(iter_)  # pyright: ignore[reportGeneralTypeIssues]  # False flag.
    finally:
        await cancel_futures(futures)

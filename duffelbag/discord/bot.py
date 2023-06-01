"""Module containing a custom bot implementation."""

# pyright: reportPrivateUsage = false

import asyncio
import typing

from disnake.ext import commands


class Duffelbag(commands.InteractionBot):
    """The custom bot implementation for Duffelbag."""

    def __init__(self, **kwargs: typing.Any) -> None:  # noqa: ANN401
        self._command_sync_delay: float = 2.0
        self._sync_task: asyncio.Task[None] | None = None
        super().__init__(**kwargs)

    async def _prepare_application_commands(self) -> None:
        if self._sync_task and not self._sync_task.done() and not self._sync_task.cancelled():
            await self._sync_task

        await self.wait_until_first_connect()
        await self._cache_application_commands()
        await self._sync_application_commands()

    async def _delayed_command_sync(self) -> None:
        if (
            not self._command_sync_flags._sync_enabled
            or not self.is_ready()
            or self._is_closed
            or self.loop.is_closed()
        ):
            return

        if self._sync_task and not self._sync_task.done() and not self._sync_task.cancelled():
            self._sync_task.cancel()

        self._sync_task = asyncio.create_task(self._sync_application_commands())

    async def _sync_application_commands(self) -> None:
        await asyncio.sleep(self._command_sync_delay)
        await super()._sync_application_commands()
        self.dispatch("command_sync", self)

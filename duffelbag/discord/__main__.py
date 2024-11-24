"""Main module to run the Duffelbag discord bot."""

import asyncio
import importlib
import pkgutil
import typing

import aiohttp
import arkprts
import disnake
import uvloop
from disnake.ext import commands, components

from duffelbag import log, shared
from duffelbag.discord import bot, config, exts, localisation, manager

# Extensions.


@typing.runtime_checkable
class _ExtensionAware(typing.Protocol):
    def setup(self, bot: commands.Bot, /) -> None:
        ...


def _discover_exts() -> typing.Generator[str, None, None]:
    def on_error(name: str) -> typing.NoReturn:
        raise ImportError(name=name)

    module_visitor = pkgutil.walk_packages(
        path=exts.__path__,  # Start at exts submodule,
        prefix=f"{exts.__name__}.",  # Prefix with exts submodule dothpath for absolute imports,
        onerror=on_error,  # Raise ImportErrors if anything unexpected happens.
    )

    for module_info in module_visitor:
        module = importlib.import_module(module_info.name)

        if isinstance(module, _ExtensionAware):
            yield module_info.name


def _make_client_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()

    shared.set_session(session)
    return session


def _make_guest_client(session: aiohttp.ClientSession) -> arkprts.Client:
    network = arkprts.NetworkSession("en", session=session)
    auth = arkprts.GuestAuth(network=network)
    client = arkprts.Client(auth=auth, assets=False)

    shared.set_guest_client(client)
    return client


def _make_intents() -> disnake.Intents:
    if config.BOT_CONFIG.DISCORD_IS_PROD:
        return disnake.Intents.none()

    return (
        disnake.Intents.messages
        | disnake.Intents.guild_messages
        | disnake.Intents.guilds
        | disnake.Intents.voice_states
        | disnake.Intents.message_content
    )


def _make_sync_flags() -> commands.CommandSyncFlags:
    if config.BOT_CONFIG.DISCORD_IS_PROD:
        return commands.CommandSyncFlags.default()

    return commands.CommandSyncFlags.default() | commands.CommandSyncFlags.sync_commands_debug


async def _main() -> None:
    duffelbag = bot.Duffelbag(
        intents=_make_intents(),
        reload=not config.BOT_CONFIG.DISCORD_IS_PROD,
        command_sync_flags=_make_sync_flags(),
    )

    root_manager = components.get_manager()
    root_manager.add_to_bot(duffelbag)

    log.initialise()
    localisation.initialise(duffelbag)
    manager.initialise()

    for ext in _discover_exts():
        duffelbag.load_extension(ext)

    async with _make_client_session() as session:
        _make_guest_client(session)

        await duffelbag.start(config.BOT_CONFIG.DISCORD_TOKEN)


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(_main())

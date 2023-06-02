"""Main module to run the Duffelbag discord bot."""

import asyncio
import importlib
import pkgutil
import typing

import disnake
import uvloop
from disnake.ext import commands, components

from duffelbag.discord import bot, config, exts, localisation

# Extensions.


@typing.runtime_checkable
class _ExtensionAware(typing.Protocol):
    def setup(self, __bot: commands.Bot) -> None:
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


async def _main() -> None:
    duffelbag = bot.Duffelbag(
        intents=disnake.Intents.none(),
        reload=not config.BOT_CONFIG.DISCORD_IS_PROD,
        sync_commands_debug=not config.BOT_CONFIG.DISCORD_IS_PROD,
    )

    manager = components.get_manager()
    manager.add_to_bot(duffelbag)

    localisation.initialise(duffelbag)

    for ext in _discover_exts():
        duffelbag.load_extension(ext)

    await duffelbag.start(config.BOT_CONFIG.DISCORD_TOKEN)


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(_main())

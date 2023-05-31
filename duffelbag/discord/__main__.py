"""Main module to run the Duffelbag discord bot."""

import asyncio
import importlib
import logging
import pkgutil
import typing

import disnake
from disnake.ext import commands, components

from duffelbag.discord import config, exts

_LOGGER = logging.getLogger("duffelbag.discord")


# Extensions.


@typing.runtime_checkable
class _ExtensionAware(typing.Protocol):
    def setup(self, __bot: commands.Bot) -> None:
        ...


def _discover_exts() -> typing.Generator[str, None, None]:
    def on_error(name: str) -> typing.NoReturn:
        raise ImportError(name=name)

    module_visitor = pkgutil.walk_packages(
        exts.__path__,
        f"{exts.__name__}.",
        onerror=on_error,
    )

    for module_info in module_visitor:
        module = importlib.import_module(module_info.name)

        if isinstance(module, _ExtensionAware):
            yield module_info.name


# Component manager callback wrapper.


async def _callback_wrapper(
    manager: components.ComponentManager,
    component: components.api.RichComponent,
    _: disnake.Interaction,
) -> typing.AsyncGenerator[None, None]:
    try:
        # Run component callback...
        yield

    except Exception as exc:
        # Log any exception...
        exc_info = type(exc), exc, exc.__traceback__.tb_next if exc.__traceback__ else None
        logging.exception(
            "An exception occurred while handling the callback for component %r:",
            manager.make_identifier(type(component)),
            exc_info=exc_info,
        )
        raise

    else:
        # Log success...
        logging.info(
            "Successfully invoked the callback component %r.",
            manager.make_identifier(type(component)),
        )


async def _main() -> None:
    bot = commands.InteractionBot(intents=disnake.Intents.none())
    manager = components.get_manager()
    manager.add_to_bot(bot)

    manager.as_callback_wrapper(_callback_wrapper)

    for ext in _discover_exts():
        bot.load_extension(ext)

    await bot.start(config.BOT_CONFIG.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(_main())

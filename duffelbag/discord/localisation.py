"""Module containing helpers for Discord-specific localisation."""

import typing

import disnake
from disnake.ext import commands

from duffelbag import localisation as base_localisation

_COMMAND_MENTION_LOCALISATIONS: dict[str, dict[str, str]] = {}


def initialise(bot: commands.InteractionBot) -> None:
    """Initialise slash command mentions."""
    bot.add_listener(repopulate_command_mentions, "on_command_sync")


def _walk_top_level_slash(
    command: commands.InvokableSlashCommand,
) -> typing.Generator[commands.InvokableSlashCommand | commands.SubCommand, None, None]:
    children = getattr(command, "children", None)
    if not children:
        yield command
    else:
        for child in children.values():
            yield from _walk_top_level_slash(child)


async def repopulate_command_mentions(bot: commands.InteractionBot) -> None:
    """Repopulate the internal cache for slash command mentions."""
    _COMMAND_MENTION_LOCALISATIONS.clear()

    for locale in base_localisation.LOCALISATION_DATA:
        _COMMAND_MENTION_LOCALISATIONS[locale] = {}

        for command in bot.global_application_commands:
            if not isinstance(command, disnake.APISlashCommand):
                continue

            slash = bot.get_slash_command(command.name)
            if not slash:
                continue

            assert isinstance(slash, commands.InvokableSlashCommand)  # noqa: S101

            for child in _walk_top_level_slash(slash):
                key = f"cmd${child.qualified_name.replace(' ', '_')}"

                # NOTE: For now, we leave mentions unlocalised.
                value = f"</{child.qualified_name}:{command.id}>"

                _COMMAND_MENTION_LOCALISATIONS[locale][key] = value


def localise(
    key: str,
    locale: disnake.Locale | str,
    *,
    strict: bool = True,
    format_map: typing.Mapping[str, object] | None = None,
) -> str:
    """Get a localised string with the provided key and locale.

    Any passed kwargs will be used to format the string.

    Parameters
    ----------
    key:
        The key of the string that is to be localised.
    locale:
        The locale to use.
    strict:
        Whether or not to require all format keys to be exhausted.
    format_map:
        A mapping used to format the localisation string.

    Returns
    -------
    str
        The localised and formatted string.
    """
    if not _COMMAND_MENTION_LOCALISATIONS:
        msg = "Localisations must be initialised first."
        raise RuntimeError(msg)

    if format_map is None:
        format_map = {}

    resolved_locale: str = locale.name if isinstance(locale, disnake.Locale) else locale

    return base_localisation.localise(
        key,
        resolved_locale,
        strict=strict,
        format_map=format_map | (_COMMAND_MENTION_LOCALISATIONS[resolved_locale]),
    )

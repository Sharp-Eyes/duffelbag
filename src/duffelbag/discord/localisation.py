"""Module containing helpers for Discord-specific localisation."""

import typing

import hikari
import tanjun

from duffelbag import localisation as base_localisation
from duffelbag import log

_LOGGER = log.get_logger(__name__)

_COMMAND_MENTION_LOCALISATIONS: dict[str, dict[str, str]] = {}


async def repopulate_command_mentions(source: tanjun.abc.Client | tanjun.Component) -> None:
    """Repopulate the internal cache for slash command mentions."""
    _LOGGER.trace("(Re)populating slash command mentions...")
    _COMMAND_MENTION_LOCALISATIONS.clear()

    if isinstance(source, tanjun.abc.Client):
        client = source
    else:
        client = source.client
        assert client is not None

    for locale in base_localisation.LOCALISATION_DATA:
        _COMMAND_MENTION_LOCALISATIONS[locale] = {}

        for component in client.components:
            for command in component.slash_commands:

                parent = command
                while parent.parent:
                    parent = parent.parent

                # for child in _walk_top_level_slash(slash):
                key = f"cmd${command.name.replace(' ', '_')}"

                # NOTE: For now, we leave mentions unlocalised.
                value = f"</{command.name}:{parent.tracked_command_id}>"

                _COMMAND_MENTION_LOCALISATIONS[locale][key] = value

    _LOGGER.warning(_COMMAND_MENTION_LOCALISATIONS)

    _LOGGER.trace("Slash command mention (re)population complete.")


def localise(
    key: str,
    locale: str | hikari.Locale,
    *,
    strict: bool = True,
    format_map: dict[str, object] | None = None,
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
    _LOGGER.trace("Localising key %r.", key)

    if not _COMMAND_MENTION_LOCALISATIONS:
        msg = "Localisations must be initialised first."
        raise RuntimeError(msg)

    if format_map is None:
        format_map = {}

    if isinstance(locale, hikari.Locale):
        locale = locale.value

    format_map |= _COMMAND_MENTION_LOCALISATIONS[locale]

    _LOGGER.trace("Target locale: %r.", locale)
    _LOGGER.debug(
        "Localisation type: %r, Localisation parameters: %r.",
        "strict" if strict else "lenient",
        format_map,
    )

    return base_localisation.localise(key, locale, strict=strict, format_map=format_map)


format_timestamp: typing.Final = base_localisation.format_timestamp

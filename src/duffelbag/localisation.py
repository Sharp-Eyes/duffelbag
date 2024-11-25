"""Module containing helpers for platform-agnostic localisation."""

import datetime as datetime_
import pathlib
import typing

import orjson

__all__: typing.Sequence[str] = ("LOCALISATION_DATA", "format_timestamp", "localise", "update_localisation_data")

DEFAULT_LOCALE: typing.Final[str] = "en_GB"
LOCALISATION_DIR: typing.Final[pathlib.Path] = pathlib.Path.cwd() / "localisation"
LOCALISATION_DATA: dict[str, dict[str, str]] = {}


class _LazyFormatDict(dict[str, object]):
    def __missing__(self, key: str) -> object:
        return f"{{{key}}}"


def update_localisation_data() -> dict[str, dict[str, str]]:
    """Update localisation data from localisation json files."""
    for file in LOCALISATION_DIR.iterdir():
        locale = file.stem
        data = orjson.loads(file.read_text())

        LOCALISATION_DATA[locale] = data

    return LOCALISATION_DATA


def localise(
    key: str,
    locale: str,
    *,
    strict: bool = True,
    format_map: typing.Mapping[str, object],
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
    if locale not in LOCALISATION_DATA or key not in LOCALISATION_DATA[locale]:
        string = LOCALISATION_DATA[DEFAULT_LOCALE][key]

    else:
        string = LOCALISATION_DATA[locale][key]

    if not strict:
        format_map = _LazyFormatDict(format_map)

    return string.format_map(format_map)


update_localisation_data()


def format_timestamp(datetime: datetime_.datetime, /, style: str) -> str:
    """Format a timestamp with discord markdown."""
    return f"<t:{datetime.timestamp():.0f}:{style}>"

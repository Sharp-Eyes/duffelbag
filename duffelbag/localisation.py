"""Module containing helpers for platform-agnostic localisation."""

import pathlib
import typing

import orjson

__all__: typing.Sequence[str] = ("LOCALISATION_DATA", "update_localisation_data", "localise")

DEFAULT_LOCALE: typing.Final[str] = "en_GB"
LOCALISATION_DIR: typing.Final[pathlib.Path] = pathlib.Path.cwd() / "localisation"
LOCALISATION_DATA: dict[str, dict[str, str]] = {}


def update_localisation_data() -> dict[str, dict[str, str]]:
    """Update localisation data from localisation json files."""
    for file in LOCALISATION_DIR.iterdir():
        locale = file.stem
        data = orjson.loads(file.read_text())

        LOCALISATION_DATA[locale] = data

    return LOCALISATION_DATA


def localise(key: str, locale: str, **kwargs: object) -> str:
    """Get a localised string with the provided key and locale.

    Any passed kwargs will be used to format the string.

    Parameters
    ----------
    key:
        The key of the string that is to be localised.
    locale:
        The locale to use.
    **kwargs:
        Keyword-arguments used to format the localisation string.

    Returns
    -------
    str
        The localised and formatted string.
    """
    if locale not in LOCALISATION_DATA or key not in LOCALISATION_DATA[locale]:
        string = LOCALISATION_DATA[DEFAULT_LOCALE][key]

    else:
        string = LOCALISATION_DATA[locale][key]

    return string.format_map(kwargs)


update_localisation_data()

"""Helper functions to fetch and parse large gamedata JSON files."""

import asyncio
import typing

import aiohttp

from . import models

_all__: typing.Sequence[str] = (
    "fetch_all",
    "fetch_characters",
    "fetch_items",
    "fetch_skills",
    "fetch_tags",
)


# fmt: off
_CHARACTER_DATA_URL: typing.Final[str] = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/en_US/gamedata/excel/character_table.json"
)
_SKILL_DATA_URL: typing.Final[str] = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/en_US/gamedata/excel/skill_table.json"
)
_ITEM_DATA_URL: typing.Final[str] = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/en_US/gamedata/excel/item_table.json"
)
_TAG_DATA_URL: typing.Final[str] = (
    "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/en_US/gamedata/excel/gacha_table.json"
)
# fmt: on


async def fetch_characters(
    session: aiohttp.ClientSession | None = None,
) -> typing.Sequence[models.RawCharacter]:
    """Download and parse character gamedata.

    Parameters
    ----------
    session:
        The session to use to fetch the data. If not provided, a new session
        is created.

    Returns
    -------
    Sequence[:class:`models.RawCharacter`]
        The parsed character models.
    """
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_characters(session)

    async with session.get(_CHARACTER_DATA_URL) as response:
        data = await response.json(content_type="text/plain")

    return [
        models.RawCharacter(**character)
        for id_, character in data.items()
        if id_.startswith("char") and not character["isNotObtainable"]
    ]


async def fetch_skills(
    session: aiohttp.ClientSession | None = None,
) -> typing.Sequence[models.RawSkill]:
    """Download and parse skill gamedata.

    Parameters
    ----------
    session:
        The session to use to fetch the data. If not provided, a new session
        is created.

    Returns
    -------
    Sequence[:class:`models.RawSkill`]
        The parsed skill models.
    """
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_skills(session)

    async with session.get(_SKILL_DATA_URL) as response:
        data = await response.json(content_type="text/plain")

    return [
        models.RawSkill(**skill)
        for id_, skill in data.items()
        if id_.startswith(("skchr", "skcom"))
    ]  # fmt: skip


async def fetch_items(
    session: aiohttp.ClientSession | None = None,
) -> typing.Sequence[models.RawItem]:
    """Download and parse item gamedata.

    Parameters
    ----------
    session:
        The session to use to fetch the data. If not provided, a new session
        is created.

    Returns
    -------
    Sequence[:class:`models.RawSkill`]
        The parsed item models.
    """
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_items(session)

    async with session.get(_ITEM_DATA_URL) as response:
        data = await response.json(content_type="text/plain")

    return [
        models.RawItem(**item)
        for _, item in data["items"].items()
        if (
            item["classifyType"] == "MATERIAL" and item["itemType"] == "MATERIAL"
            or item["classifyType"] == "NORMAL" and item["itemType"] == "GOLD"
        )  # fmt: skip
    ]


async def fetch_tags(
    session: aiohttp.ClientSession | None = None,
) -> typing.Sequence[models.RawTag]:
    """Download and parse character tag gamedata.

    Parameters
    ----------
    session:
        The session to use to fetch the data. If not provided, a new session
        is created.

    Returns
    -------
    Sequence[:class:`models.RawSkill`]
        The parsed tag models.
    """
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_tags(session)

    async with session.get(_TAG_DATA_URL) as response:
        data = await response.json(content_type="text/plain")

    return [models.RawTag(**tag) for tag in data["gachaTags"]]


async def fetch_all(
    session: aiohttp.ClientSession | None = None,
) -> tuple[
    typing.Sequence[models.RawCharacter],
    typing.Sequence[models.RawSkill],
    typing.Sequence[models.RawItem],
]:
    """Download and parse character, skill, item and tag gamedata.

    Parameters
    ----------
    session:
        The session to use to fetch the data. If not provided, a new session
        is created. The same session is used for all individual data types.

    Returns
    -------
    tuple[Sequence[:class:`models.RawCharacter`], Sequence[:class:`models.RawCharacter`], Sequence[:class:`models.RawItem`], Sequence[:class:`models.RawTag`]
        The parsed models.
    """  # noqa: E501
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_all(session)

    async with aiohttp.ClientSession() as session:
        characters, skills, items = await asyncio.gather(
            fetch_characters(session),
            fetch_skills(session),
            fetch_items(session),
        )

    return characters, skills, items

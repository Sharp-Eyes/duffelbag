"""Module that provides entrypoints to globally available stuff."""

import typing

import aiohttp
import arkprts

import database

_VALID_SERVERS = frozenset(arkprts.network.NETWORK_ROUTES)


_session: aiohttp.ClientSession | None = None
_guest_client: arkprts.Client | None = None

# TODO: probably add TTL.
_client_cache: dict[tuple[arkprts.ArknightsServer, str], arkprts.Client] = {}


def validate_server(server: str) -> typing.TypeGuard[arkprts.ArknightsServer]:
    """Check whether a string is a valid Arknights server."""
    return server in _VALID_SERVERS


def get_session() -> aiohttp.ClientSession:
    """Set the shared global ClientSession.

    Can only be used after a ClientSession was set using `set_session`.
    """
    if _session:
        return _session

    msg = "The global ClientSession has not yet been set."
    raise RuntimeError(msg)


def set_session(client_session: aiohttp.ClientSession) -> None:
    """Get the shared global ClientSession."""
    global _session  # noqa: PLW0603

    _session = client_session


def get_guest_client() -> arkprts.Client:
    """Get the shared global arkprts guest Client.

    Can only be used after a ClientSession was set using `set_session`.
    """
    if _guest_client:
        return _guest_client

    msg = "The global guest Client has not yet been set."
    raise RuntimeError(msg)


def set_guest_client(guest_client: arkprts.Client) -> None:
    """Set the shared global arkprts guest Client."""
    global _guest_client  # noqa: PLW0603

    _guest_client = guest_client


def get_network() -> arkprts.NetworkSession:
    """Get the shared global arkprts NetworkSession.

    Can only be used after a ClientSession was set using `set_session`.
    """
    return get_guest_client().network


async def make_user_client(
    server: arkprts.ArknightsServer,
    channel_uid: str,
    token: str,
) -> arkprts.Client:
    """Make a new arkprts user Client with default configuration options.

    Can only be used after a ClientSession was set using `set_session`.
    """
    return await arkprts.Client.from_token(
        channel_uid=channel_uid,
        token=token,
        server=server,
        network=get_network(),
        assets=False,
    )


def get_user_client(server: arkprts.ArknightsServer, channel_uid: str) -> arkprts.Client | None:
    """Get a cached arkprts user client."""
    return _client_cache.get((server, channel_uid))


def set_user_client(
    server: arkprts.ArknightsServer,
    channel_uid: str,
    client: arkprts.Client,
) -> None:
    """Cache an arkprts user Client."""
    _client_cache[server, channel_uid] = client


async def ensure_user_client(arknights_user: database.ArknightsUser) -> arkprts.Client:
    """Get a cached user client if it exists, create a new one otherwise."""
    assert validate_server(arknights_user.server)

    if client := get_user_client(arknights_user.server, arknights_user.channel_uid):
        return client

    client = await make_user_client(
        arknights_user.server,
        arknights_user.channel_uid,
        arknights_user.yostar_token,
    )
    set_user_client(arknights_user.server, arknights_user.channel_uid, client)

    return client

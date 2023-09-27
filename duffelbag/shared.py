"""Module that provides entrypoints to globally available stuff."""

import aiohttp
import arkprts

_session: aiohttp.ClientSession | None = None
_guest_client: arkprts.Client | None = None

# TODO: probably add TTL.
_client_cache: dict[tuple[arkprts.ArknightsServer, str], arkprts.Client] = {}


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
    """Get the shared global arkprts NetworkSession."""
    return get_guest_client().network


def get_user_client(server: arkprts.ArknightsServer, uid: str) -> arkprts.Client | None:
    """Get a cached arkprts user client."""
    return _client_cache.get((server, uid))


def set_user_client(server: arkprts.ArknightsServer, uid: str, client: arkprts.Client) -> None:
    """Cache an arkprts user Client."""
    _client_cache[server, uid] = client

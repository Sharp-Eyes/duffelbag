"""Main module to run the Duffelbag discord bot."""

import asyncio

import aiohttp
import arkprts
import hikari
import ryoshu
import tanjun
import uvloop

from duffelbag import log, shared
from duffelbag.discord import config, manager

# Extensions.


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


def _make_intents() -> hikari.Intents:
    if config.BOT_CONFIG.DISCORD_IS_PROD:
        return hikari.Intents.NONE

    return (
        hikari.Intents.DM_MESSAGES
        | hikari.Intents.GUILD_MESSAGES
        | hikari.Intents.GUILDS
        | hikari.Intents.MESSAGE_CONTENT
    )


async def _main() -> None:
    duffelbag = hikari.GatewayBot(
        token = config.BOT_CONFIG.DISCORD_TOKEN,
        intents=_make_intents(),
    )

    root_manager = ryoshu.get_manager()
    root_manager.add_to_bot(duffelbag)

    log.initialise()
    # localisation.initialise(duffelbag)
    manager.initialise()

    # for ext in _discover_exts():
    #     duffelbag.load_extension(ext)

    async with _make_client_session() as session:
        _make_guest_client(session)

        client = (
            tanjun.Client.from_gateway_bot(duffelbag)
            .set_type_dependency(aiohttp.ClientSession, session)
        )

        await duffelbag.start()



if __name__ == "__main__":
    uvloop.install()
    asyncio.run(_main())

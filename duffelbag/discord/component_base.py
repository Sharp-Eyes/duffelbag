"""Shared component base classes for duffelbag."""

import asyncio
import typing

import arkprts
import disnake
from disnake.ext import components

import database
from duffelbag import auth, shared

__all__: typing.Sequence[str] = ("ArknightsAccountSelect",)

_ServerToApiUserDict = dict[arkprts.ArknightsServer, typing.Sequence[arkprts.models.PartialPlayer]]


class ArknightsAccountSelect(components.RichStringSelect, typing.Protocol):
    """Select menu base class to pick an Arknights account."""

    # TODO: Pagination? Limit accounts to 25? Who knows.

    sep: typing.ClassVar[str] = "|"

    placeholder: str = "Select an account..."
    min_values: int = 1
    max_values: int = 1

    @classmethod
    def make_option_from_account(
        cls,
        account: database.ArknightsUser,
        display_name: str | None = None,
    ) -> disnake.SelectOption:
        """Make a SelectOption for this select given an ArknightsUser."""
        if not display_name:
            display_name = account.game_uid

        return disnake.SelectOption(
            label=f"{display_name} [{account.server}]",
            value=f"{account.server}{cls.sep}{account.game_uid}",
            default=account.active,
        )

    @classmethod
    async def from_arknights_accounts(
        cls,
        arknights_accounts: typing.Sequence[database.ArknightsUser],
    ) -> typing.Self:
        """Make a select menu from a list of Arknights accounts."""
        accounts_by_server: dict[arkprts.ArknightsServer, list[database.ArknightsUser]] = {}
        for account in arknights_accounts:
            server = typing.cast(arkprts.ArknightsServer, account.server)
            if server not in accounts_by_server:
                accounts_by_server[server] = []

            accounts_by_server[server].append(account)

        # TODO: Make sure this doesn't explode for non-global users.
        guest_client = shared.get_guest_client()
        users_by_server: _ServerToApiUserDict = dict(
            zip(  # Recombine asyncio.gather output with accounts_by_server keys.
                accounts_by_server,
                await asyncio.gather(
                    *[
                        guest_client.get_partial_players(
                            [account.game_uid for account in accounts],
                            server=server,
                        )
                        for server, accounts in accounts_by_server.items()
                    ],
                ),
                strict=True,
            ),
        )

        options: list[disnake.SelectOption] = []
        for server, accounts in accounts_by_server.items():
            user_data = users_by_server[server]
            for account, user in zip(accounts, user_data, strict=True):
                options.append(
                    cls.make_option_from_account(
                        account,
                        display_name=f"{user.nickname}#{user.nick_number}",
                    ),
                )

        if len(options) == 1:
            # If there's only one option, ensure it can be clicked.
            options[0].default = False

        return cls(options=options)

    @classmethod
    async def for_duffelbag_user(cls, duffelbag_user: database.DuffelbagUser) -> typing.Self:
        """Make a select menu for a given Duffelbag account."""
        arknights_accounts = await auth.list_arknights_accounts(duffelbag_user)
        return await cls.from_arknights_accounts(arknights_accounts)

    @classmethod
    async def get_selected_user(cls, inter: disnake.MessageInteraction) -> database.ArknightsUser:
        """Get the selected Arknights user from an interaction."""
        assert inter.values  # min_values is 1 so cannot be none.

        server, game_uid = inter.values[0].split(cls.sep)

        return await auth.get_arknights_account_by_server_uid(
            typing.cast(arkprts.ArknightsServer, server),
            game_uid,
        )

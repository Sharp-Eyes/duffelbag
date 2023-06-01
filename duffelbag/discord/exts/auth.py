"""Bot plugin for Discord <-> Arknights user authentication."""

import typing

import attr
import disnake
from disnake.ext import commands, components, plugins

from duffelbag import auth, exceptions
from duffelbag.discord import localisation

plugin = plugins.Plugin()
manager = components.get_manager(__name__)


@plugin.slash_command()
async def account(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


_PASS_PARAM = commands.Param(
    min_length=auth.MIN_PASS_LEN,
    max_length=auth.MAX_PASS_LEN,
    description=(
        f"The password to use. Must be between {auth.MIN_PASS_LEN} and"
        f" {auth.MAX_PASS_LEN} characters long."
    ),
)


@account.sub_command(name="recover")  # pyright: ignore[reportUnknownMemberType]
async def recover_account(inter: disnake.CommandInteraction, password: str = _PASS_PARAM) -> None:
    """Recover the Duffelbag account connected to your discord account by setting a new password."""
    duffelbag_user = await auth.recover_user(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        password=password,
    )

    await inter.response.send_message(
        localisation.localise(
            "auth_recover",
            inter.locale,
            format_map={"username": duffelbag_user.username, "password": password},
        ),
        ephemeral=True,
    )


@recover_account.error  # pyright: ignore  # noqa: PGH003
async def recover_account_handler(
    inter: disnake.Interaction, exception: commands.CommandInvokeError
) -> None:
    """Handle invalid recovery attempts.

    This handles exceptions raised by `auth.recover_user`. We don't need to
    handle `ValueError`s because of slash command input validation.
    """
    exception = getattr(exception, "original", exception)

    if isinstance(exception, exceptions.UserNotFound):
        await inter.response.send_message(
            "You do not appear to have registered a Duffelbag account.",
            ephemeral=True,
        )
        return

    raise


_USER_PARAM = commands.Param(
    min_length=auth.MIN_USER_LEN,
    max_length=auth.MAX_USER_LEN,
    description=(
        f"The username to use. Must be between {auth.MIN_USER_LEN} and"
        f" {auth.MAX_USER_LEN} characters long."
    ),
)


@account.sub_command(name="create")  # pyright: ignore[reportUnknownMemberType]
async def account_create(
    inter: disnake.CommandInteraction,
    username: str = _USER_PARAM,
    password: str = _PASS_PARAM,
) -> None:
    """Create a new Duffelbag account and bind your discord account to it."""
    await auth.create_user(
        username=username,
        password=password,
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
    )

    wrapped = components.wrap_interaction(inter)

    await wrapped.response.send_message(
        localisation.localise(
            "auth_new_collapsed",
            inter.locale,
            format_map={"username": username},
        ),
        components=ExpandButton(key_base="auth_new", params=[username], collapsed=True),
        ephemeral=True,
    )


# TODO: Move this to some separate file.
_EXPAND: typing.Final[tuple[str, str, str]] = (
    "Expand...",
    "<:expand:1113954208014684252>",
    "_collapsed",
)
_COLLAPSE: typing.Final[tuple[str, str, str]] = (
    "Collapse...",
    "<:collapse:1113954205766537226>",
    "_expanded",
)


class _StringListParser(components.Parser[list[str]]):
    # TODO: Implement list support into ext-components :trol:

    def loads(self, _: disnake.Interaction, arg: str) -> list[str]:
        return arg.split(",")

    def dumps(self, arg: list[str]) -> str:
        return ",".join(arg)


class _PosToFormatMap(dict[str, object]):
    def __init__(self, *args: object, strict: bool = True) -> None:
        self._arg_iter = iter(args)
        self.strict = strict

        super().__init__()

    def __missing__(self, key: str) -> object:
        if not self.strict:
            return next(self._arg_iter, f"{{{key}}}")
        return next(self._arg_iter)


@manager.register
class ExpandButton(components.RichButton):
    """A button that toggles a message between expanded and collapsed state."""

    # Start collapsed, so show expand label and emoji.
    label: str = _EXPAND[0]
    emoji: str = _EXPAND[1]

    # Custom id params:
    key_base: str
    params: list[str] = components.field(
        attr.NOTHING, parser=_StringListParser()  # pyright: ignore[reportGeneralTypeIssues]
    )
    collapsed: bool

    def _format(self, string: str) -> str:
        return string.format_map(_PosToFormatMap(*self.params, strict=False))

    async def callback(self, inter: components.MessageInteraction) -> None:
        """Toggle between expanded/collapsed."""
        self.collapsed ^= True
        self.label, self.emoji, key_ext = _EXPAND if self.collapsed else _COLLAPSE

        message = localisation.localise(
            self.key_base + key_ext,
            inter.locale,
            strict=False,
        )

        await inter.response.edit_message(self._format(message), components=self)


@account.sub_command_group(name="bind")  # pyright: ignore[reportUnknownMemberType]
async def account_bind(_: disnake.CommandInteraction) -> None:
    """Bind an account."""


@account_bind.sub_command(name="platform")  # pyright: ignore[reportUnknownMemberType]
async def account_bind_platform(inter: disnake.CommandInteraction) -> None:
    """Bind your Discord account to a Duffelbag account."""
    await inter.response.send_message("Your mother.")


setup, teardown = plugin.create_extension_handlers()

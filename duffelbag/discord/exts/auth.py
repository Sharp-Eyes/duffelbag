"""Bot plugin for Discord <-> Arknights user authentication."""

import disnake
from disnake.ext import commands, plugins

from duffelbag import auth, exceptions

plugin = plugins.Plugin()


@plugin.slash_command()
async def account(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


_PASS_PARAM = commands.Param(
    min_length=auth.MIN_PASS_LEN,
    max_length=auth.MAX_PASS_LEN,
    description=(
        f"The new password to use. Must be between {auth.MIN_PASS_LEN} and"
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
        "## Password updated!\nYour Duffelbag account with name"
        f" **{duffelbag_user.username}** has been updated to use password"
        f" ||{password}||.",
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


setup, teardown = plugin.create_extension_handlers()

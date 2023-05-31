"""Bot plugin for Discord <-> Arknights user authentication."""

import disnake
from disnake.ext import commands, plugins

from duffelbag import auth

plugin = plugins.Plugin()


@plugin.slash_command()
async def account(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


@account.sub_command(name="recover")  # pyright: ignore[reportUnknownMemberType]
async def recover_account(
    inter: disnake.CommandInteraction,
    password: str = commands.Param(max_length=32),  # noqa: B008
) -> None:
    """Recover the Duffelbag account connected to your discord account by setting a new password."""
    duffelbag_user = await auth.recover_users(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        password=password,
    )

    await inter.response.send_message(
        f"## Password updated!\nDuffelbag account **{duffelbag_user.username}**'s"
        f" password has been updated to ||{password}||.",
        ephemeral=True,
    )


@recover_account.error  # pyright: ignore  # noqa: PGH003
async def recover_account_handler(
    inter: disnake.Interaction, exception: commands.CommandInvokeError
) -> None:
    """Handle invalid recovery attempts."""
    exception = getattr(exception, "original", exception)

    if isinstance(exception, RuntimeError):
        await inter.response.send_message(
            "You do not appear to have registered a Duffelbag account.",
            ephemeral=True,
        )
        return

    raise


setup, teardown = plugin.create_extension_handlers()

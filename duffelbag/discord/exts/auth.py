"""Bot plugin for Discord <-> Arknights user authentication."""

import disnake
from disnake.ext import commands, plugins

from duffelbag import auth

plugin = plugins.Plugin()


@plugin.slash_command()
async def account(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


@account.sub_command(name="recover")  # pyright: ignore[reportUnknownMemberType]
async def recover_account(inter: disnake.CommandInteraction) -> None:
    """Recover all Duffelbag accounts connected to your discord account."""
    # TODO: Pagination for >25 (field limit) accounts.
    #       Probably actually start paginating at considerably fewer accounts.
    #       Maybe setup KeyDB for this?

    duffelbag_users = await auth.recover_users(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
    )

    embed = (
        disnake.Embed(
            title="Account Recovery",
            description="Passwords are hidden under spoiler tags."
        )
        .set_author(name=inter.author.name, icon_url=inter.author.display_avatar)
    )  # fmt: skip

    for user in duffelbag_users:
        embed.add_field(
            name="\u200b",
            value=f"Username: {user.username}\nPassword: ||{user.password}||",
        )

    await inter.response.send_message(embed=embed, ephemeral=True)


@recover_account.error  # pyright: ignore  # noqa: PGH003
async def recover_account_handler(
    inter: disnake.Interaction, exception: commands.CommandInvokeError
) -> bool:
    """Handle invalid recovery attempts."""
    exception = getattr(exception, "original", exception)

    if isinstance(exception, RuntimeError):
        await inter.response.send_message(
            "You do not appear to have any registered Duffelbag accounts.",
            ephemeral=True,
        )
        return True

    raise


setup, teardown = plugin.create_extension_handlers()

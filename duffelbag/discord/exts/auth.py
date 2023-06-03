"""Bot plugin for Discord <-> Arknights user authentication."""

import disnake
from disnake.ext import commands, components, plugins

from duffelbag import auth, exceptions
from duffelbag.discord import localisation

plugin = plugins.Plugin()
external_manager = components.get_manager("duffelbag.restricted")


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
        components=external_manager.make_button(
            "ExpBut", key_base="auth_new", params=[username, auth.Platform.DISCORD.value]
        ),
        ephemeral=True,
    )


# TODO: Move this to some separate file.


@account.sub_command_group(name="bind")  # pyright: ignore[reportUnknownMemberType]
async def account_bind(_: disnake.CommandInteraction) -> None:
    """Bind an account."""


@account_bind.sub_command(name="platform")  # pyright: ignore[reportUnknownMemberType]
async def account_bind_platform(inter: disnake.CommandInteraction) -> None:
    """Bind your Discord account to a Duffelbag account."""
    await inter.response.send_message("Your mother.")


@recover_account.error  # pyright: ignore  # noqa: PGH003
@account_create.error  # pyright: ignore  # noqa: PGH003
@account_bind_platform.error  # pyright: ignore  # noqa: PGH003
async def recover_account_handler(
    inter: disnake.Interaction, exception: commands.CommandInvokeError
) -> None:
    """Handle invalid recovery attempts.

    This handles exceptions raised by `auth.recover_user`.
    """
    # TODO: Move error message text to localisation files.
    exception = getattr(exception, "original", exception)

    if isinstance(exception, exceptions.UserNotFound):
        await inter.response.send_message(
            "You do not appear to have registered a Duffelbag account.",
            ephemeral=True,
        )
        return

    if isinstance(exception, ValueError):
        await inter.response.send_message(str(exception), ephemeral=True)

    raise


setup, teardown = plugin.create_extension_handlers()

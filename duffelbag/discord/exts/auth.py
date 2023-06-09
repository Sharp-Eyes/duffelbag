"""Bot plugin for Discord <-> Arknights user authentication."""

import typing

import disnake
from disnake.ext import commands, components, plugins
from disnake.ext.components import interaction as interaction_

from duffelbag import auth, exceptions, log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)

# TODO: Expose a type like this in ext-components somewhere
_MessageComponents = interaction_.Components[interaction_.MessageComponents]


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
            "ExpBut",
            key_base="auth_new",
            params=[username, auth.Platform.DISCORD.value],
        ),
        ephemeral=True,
    )


@account.sub_command_group(name="bind")  # pyright: ignore[reportUnknownMemberType]
async def account_bind(_: disnake.CommandInteraction) -> None:
    """Bind an account."""


@account_bind.sub_command(name="platform")  # pyright: ignore[reportUnknownMemberType]
async def account_bind_platform(
    inter: disnake.CommandInteraction,
    username: str = _USER_PARAM,
    password: str = _PASS_PARAM,
) -> None:
    """Bind your Discord account to an existing Duffelbag account."""
    duffelbag_user = await auth.login_user(username=username, password=password)

    await auth.add_platform_account(
        duffelbag_user,
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
    )

    await inter.response.send_message(
        localisation.localise(
            "auth_bind",
            locale=inter.locale,
            format_map={
                "platform": auth.Platform.DISCORD.value,
                "username": username,
            },
        ),
        ephemeral=True,
    )


@account.error  # pyright: ignore  # noqa: PGH003
async def account_error_handler(
    inter: disnake.Interaction,
    exception: commands.CommandInvokeError,
) -> typing.Literal[True]:
    """Handle invalid recovery attempts.

    This handles exceptions raised by `auth.recover_user`.
    """
    _LOGGER.trace(
        "Handling auth exception of type %r for user %r.",
        type(exception).__name__,
        inter.author.id,
    )
    exception = getattr(exception, "original", exception)

    params: dict[str, object] = {}
    msg_components: _MessageComponents = []

    match exception:
        case exceptions.CredentialSizeViolation():
            key = "exc_auth_credsize"

        case exceptions.CredentialCharacterViolation():
            key = "exc_auth_credchar"

        case exceptions.AuthStateError(in_progress=in_progress):
            key = "exc_auth_inprog" if in_progress else "exc_auth_noprog"

        case exceptions.DuffelbagUserExists(username=username):
            key = "exc_auth_dfb_exists_collapsed"
            msg_components.append(
                external_manager.make_button(
                    "ExpBut",
                    key_base="exc_auth_dfb_exists",
                    params=[username],
                )
            )

        case exceptions.DuffelbagLoginFailure():
            key = "exc_auth_dfb_loginfail"

        case exceptions.PlatformLoginFailure():
            key = "exc_auth_pf_loginfail"

        case exceptions.PlatformConnectionExists(is_own=is_own):
            key = "exc_auth_pf_exists_self" if is_own else "exc_auth_pf_exists"
            params["platform"] = auth.Platform.DISCORD.value

        case exceptions.ArknightsConnectionExists(is_own=is_own):
            key = "exc_auth_ak_exists_self" if is_own else "exc_auth_ak_exists"

        case _:
            _LOGGER.trace("Exception went unhandled in local error handler.")
            raise

    params |= exception.to_dict()
    wrapped = components.wrap_interaction(inter)

    await wrapped.response.send_message(
        localisation.localise(key, inter.locale, format_map=params),
        components=msg_components,
        ephemeral=True,
    )

    _LOGGER.trace("Exception handled successfully in local error handler.")
    return True


setup, teardown = plugin.create_extension_handlers()

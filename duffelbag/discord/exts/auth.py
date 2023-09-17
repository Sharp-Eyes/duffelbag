"""Bot plugin for Discord <-> Arknights user authentication."""

import asyncio
import datetime
import re
import typing

import disnake
from disnake.ext import commands, components, plugins
from disnake.ext.components import interaction as interaction_

import database
from duffelbag import async_utils, auth, exceptions, log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)
_EMAIL_REGEX: typing.Final[typing.Pattern[str]] = re.compile(
    # https://stackoverflow.com/a/201378
    r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$",
)

# TODO: Expose a type like this in ext-components somewhere
_MessageComponents = interaction_.Components[interaction_.MessageComponents]


plugin = plugins.Plugin()
manager = components.get_manager("duffelbag")


@plugin.slash_command()
async def account(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


@account.sub_command_group(name="duffelbag")  # pyright: ignore
async def account_duffelbag(_: disnake.CommandInteraction) -> None:
    """Do stuff with Duffelbag accounts."""


_USER_PARAM = commands.Param(
    min_length=auth.MIN_USER_LEN,
    max_length=auth.MAX_USER_LEN,
    description=(
        f"The username to use. Must be between {auth.MIN_USER_LEN} and"
        f" {auth.MAX_USER_LEN} characters long."
    ),
)


_PASS_PARAM = commands.Param(
    min_length=auth.MIN_PASS_LEN,
    max_length=auth.MAX_PASS_LEN,
    description=(
        f"The password to use. Must be between {auth.MIN_PASS_LEN} and"
        f" {auth.MAX_PASS_LEN} characters long."
    ),
)


@account_duffelbag.sub_command(name="create")  # pyright: ignore
async def account_duffelbag_create(
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
        components=manager.make_button(
            "ExpBtn",
            key_base="auth_new",
            params=[username, auth.Platform.DISCORD.value],
        ),
        ephemeral=True,
    )


@account_duffelbag.sub_command(name="recover")  # pyright: ignore
async def account_duffelbag_recover(
    inter: disnake.CommandInteraction,
    password: str = _PASS_PARAM,
) -> None:
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


@account_duffelbag.sub_command(name="delete")  # pyright: ignore
async def account_duffelbag_delete(
    inter: disnake.CommandInteraction,
    password: str = _PASS_PARAM,
) -> None:
    """Delete your duffelbag account. This has a 24 hour grace period."""
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )

    scheduled_deletion = await auth.schedule_user_deletion(duffelbag_user, password=password)
    schedule_user_deletion(scheduled_deletion)

    await inter.response.send_message(
        localisation.localise(
            "auth_delete_schedule",
            inter.locale,
            format_map={
                "timestamp": disnake.utils.format_dt(scheduled_deletion.deletion_ts, style="R"),
            },
        ),
        ephemeral=True,
    )


@account.sub_command_group(name="bind")  # pyright: ignore
async def account_bind(_: disnake.CommandInteraction) -> None:
    """Bind an account."""


@account_bind.sub_command(name="platform")  # pyright: ignore
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
            "auth_bind_platform",
            locale=inter.locale,
            format_map={
                "platform": auth.Platform.DISCORD.value,
                "username": username,
            },
        ),
        ephemeral=True,
    )


@account_bind.sub_command(name="arknights")  # pyright: ignore
async def account_bind_arknights(
    inter: disnake.CommandInteraction,
    email: str,
) -> None:
    """Bind an Arknights account to your Duffelbag account."""
    await inter.response.defer(ephemeral=True)

    if not _EMAIL_REGEX.fullmatch(email):
        msg = f"The provided email address {email!r} is not a valid email address."
        raise exceptions.InvalidEmailError(msg, email=email)

    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )

    await auth.start_authentication(duffelbag_user, email=email)

    button = ArknightsBindButton(
        label=localisation.localise("auth_bind_ak_title", locale=inter.locale),
        email=email,
    )

    wrapped = components.wrap_interaction(inter)

    await wrapped.edit_original_message(
        localisation.localise(
            "auth_bind_ak",
            locale=inter.locale,
            format_map={"email": email},
        ),
        components=[button],
    )


@manager.register(identifier="ArkBind")
class ArknightsBindButton(components.RichButton):
    """Button to complete the Arknights account verification process."""

    label: str
    style: disnake.ButtonStyle = disnake.ButtonStyle.success

    email: str

    async def callback(self, inter: components.MessageInteraction) -> None:
        """Verify and link an Arknights account to a Duffelbag account."""
        custom_id = f"arknights_verify|{inter.id}"
        text_input = disnake.ui.TextInput(
            label=localisation.localise("auth_bind_ak_modal_label", inter.locale),
            custom_id="verification_code",
            min_length=6,
            max_length=6,
            placeholder="XXXXXX",
        )
        await inter.response.send_modal(
            title=self.label,
            custom_id=custom_id,
            components=[text_input],
        )

        # NOTE: asyncio.TimeoutError is handled by the component manager.
        modal_inter: disnake.ModalInteraction = await inter.bot.wait_for(
            disnake.Event.modal_submit,
            check=lambda modal_inter: modal_inter.custom_id == custom_id,
            timeout=5 * 60,
        )

        await modal_inter.response.defer(ephemeral=True)

        verification_code = modal_inter.text_values[text_input.custom_id]
        if not verification_code.isdigit():
            await modal_inter.edit_original_response(
                localisation.localise(
                    "auth_bind_ak_invalid_vcode",
                    locale=inter.locale,
                    format_map={"code": verification_code},
                ),
            )
            return

        duffelbag_user = await auth.get_user_by_platform(
            platform=auth.Platform.DISCORD,
            platform_id=inter.author.id,
            strict=True,
        )

        await auth.complete_authentication(
            duffelbag_user,
            email=self.email,
            verification_code=verification_code,
        )

        await modal_inter.edit_original_response(
            localisation.localise("auth_bind_ak_success", locale=inter.locale),
        )


@account.error  # pyright: ignore
async def account_error_handler(
    inter: disnake.Interaction,
    exception: commands.CommandInvokeError,
) -> typing.Literal[True]:
    """Handle invalid recovery attempts.

    This handles exceptions raised by `auth.recover_user`.
    """
    exception = getattr(exception, "original", exception)
    _LOGGER.trace(
        "Handling auth exception of type %r for user %r.",
        type(exception).__name__,
        inter.author.id,
    )

    params: dict[str, object] = {}
    msg_components: _MessageComponents = []

    match exception:
        case exceptions.CredentialSizeViolationError():
            key = "exc_auth_credsize"

        case exceptions.CredentialCharacterViolationError():
            key = "exc_auth_credchar"

        case exceptions.DuffelbagUserExistsError(username=username):
            key = "exc_auth_dfb_exists_collapsed"
            msg_components.append(
                manager.make_button(
                    "ExpBut",
                    key_base="exc_auth_dfb_exists",
                    params=[username],
                ),
            )

        case exceptions.DuffelbagLoginError():
            key = "exc_auth_dfb_loginfail"

        case exceptions.PlatformLoginError():
            key = "exc_auth_pf_loginfail"

        case exceptions.PlatformConnectionExistsError(is_own=is_own):
            key = "exc_auth_pf_exists_self" if is_own else "exc_auth_pf_exists"
            params["platform"] = auth.Platform.DISCORD.value

        case exceptions.ArknightsConnectionExistsError(is_own=is_own):
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


async def _delayed_user_deletion(scheduled_deletion: database.ScheduledUserDeletion) -> None:
    timedelta = scheduled_deletion.deletion_ts - datetime.datetime.now(tz=datetime.UTC)
    await asyncio.sleep(timedelta.total_seconds())

    duffelbag_user = await auth.get_scheduled_user_deletion_user(scheduled_deletion)
    accounts = await auth.list_connected_accounts(duffelbag_user, platform=auth.Platform.DISCORD)

    for account in accounts:
        try:
            user = await plugin.bot.get_or_fetch_user(account.platform_id, strict=True)
            await user.send(
                localisation.localise(
                    "auth_delete_success",
                    disnake.Locale.en_GB,  # TODO: figure out some way of getting locale information
                    format_map={"username": duffelbag_user.username},
                ),
            )

        except disnake.HTTPException:
            _LOGGER.warning(
                "Failed to notify Discord user with id %i of their Duffelbag account deletion.",
                account.platform_id,
            )

    await duffelbag_user.remove()


def schedule_user_deletion(scheduled_deletion: database.ScheduledUserDeletion) -> None:
    """Create a user deletion background task for a provided ScheduledUserDeletion."""
    async_utils.safe_task(_delayed_user_deletion(scheduled_deletion))


@plugin.load_hook()
async def schedule_user_deletions() -> None:
    """Get scheduled user deletions and create tasks for them."""
    scheduled_deletions = await auth.get_scheduled_user_deletions()

    for scheduled_deletion in scheduled_deletions:
        schedule_user_deletion(scheduled_deletion)


setup, teardown = plugin.create_extension_handlers()

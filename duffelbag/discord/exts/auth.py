"""Bot plugin for Discord <-> Arknights user authentication."""

import asyncio
import datetime
import re
import typing

import arkprts
import disnake
from disnake.ext import commands, components, plugins
from disnake.ext.components import interaction as interaction_

import database
from duffelbag import async_utils, auth, exceptions, log, shared
from duffelbag.discord import component_base, localisation

_LOGGER = log.get_logger(__name__)
_EMAIL_REGEX: typing.Final[typing.Pattern[str]] = re.compile(
    # https://stackoverflow.com/a/201378
    r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$",
)

# TODO: Expose a type like this in ext-components somewhere
_MessageComponents = interaction_.Components[interaction_.MessageComponents]

plugin = plugins.Plugin()
manager = components.get_manager("duffelbag.auth")


# Account manipulation commands.


@plugin.slash_command(name="account")
async def account_(_: disnake.CommandInteraction) -> None:
    """Do stuff with accounts."""


@account_.sub_command_group(name="duffelbag")  # pyright: ignore
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

    auth.verify_password(duffelbag_user=duffelbag_user, password=password)

    scheduled_deletion = await auth.schedule_user_deletion(duffelbag_user)
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


@account_.sub_command_group(name="discord")  # pyright: ignore
async def account_discord(_: disnake.CommandInteraction) -> None:
    """Do stuff with a Discord account."""


@account_discord.sub_command(name="bind")  # pyright: ignore
async def account_discord_bind(
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


@account_.sub_command_group(name="arknights")  # pyright: ignore
async def account_arknights(_: disnake.CommandInteraction) -> None:
    """Do stuff with an Arknights account."""


@account_arknights.sub_command(name="bind")  # pyright: ignore
async def account_arknights_bind(
    inter: disnake.CommandInteraction,
    server: arkprts.ArknightsServer,
    email: str,
) -> None:
    """Bind an Arknights account to your Duffelbag account."""
    await inter.response.defer(ephemeral=True)

    if not _EMAIL_REGEX.fullmatch(email):
        msg = f"The provided email address {email!r} is not a valid email address."
        raise exceptions.InvalidEmailError(msg, email=email)

    await auth.start_authentication(server=server, email=email)

    button = ArknightsBindButton(
        label=localisation.localise("auth_bind_ak_title", locale=inter.locale),
        server=server,
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


@account_arknights.sub_command(name="set-active")  # pyright: ignore
async def account_arknights_set_active(inter: disnake.CommandInteraction) -> None:
    """Set a different Arknights account as your active account."""
    await inter.response.defer(ephemeral=True)

    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )
    component = await ArknightsActiveAccountSelect.for_duffelbag_user(duffelbag_user)

    wrapped = components.wrap_interaction(inter)
    await wrapped.edit_original_response(
        localisation.localise("auth_ak_set_active", inter.locale),
        components=[component],
    )


@account_arknights.sub_command(name="unbind")  # pyright: ignore
async def account_arknights_unbind(
    inter: disnake.CommandInteraction,
    password: str = _PASS_PARAM,
) -> None:
    """Unlink your Arknights account. This has a 24 hour grace period."""
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )

    auth.verify_password(duffelbag_user=duffelbag_user, password=password)

    component = await ArknightsRemoveAccountSelect.for_duffelbag_user(duffelbag_user)

    wrapped = components.wrap_interaction(inter)
    await wrapped.response.send_message(
        localisation.localise("auth_ak_remove_msg", inter.locale),
        components=[component],
        ephemeral=True,
    )


# Account manipulation components.


@manager.register(identifier="ArkBind")
class ArknightsBindButton(components.RichButton):
    """Button to complete the Arknights account verification process."""

    label: str
    style: disnake.ButtonStyle = disnake.ButtonStyle.success

    server: arkprts.ArknightsServer = components.field(
        parser=components.parser.StringParser,  # pyright: ignore  # TODO: implement literal parser
    )
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

        arknights_user = await auth.complete_authentication(
            duffelbag_user,
            server=self.server,
            email=self.email,
            verification_code=verification_code,
        )

        await modal_inter.edit_original_response(
            localisation.localise(
                "auth_bind_ak_success_active" if arknights_user.active else "auth_bind_ak_success",
                locale=inter.locale,
            ),
        )


@manager.register(identifier="ArkActive")
class ArknightsActiveAccountSelect(component_base.ArknightsAccountSelect):
    """Select menu to set a user's active Arknights account."""

    async def callback(self, inter: components.MessageInteraction) -> None:
        """Select an Arknights account to mark as active."""
        arknights_user = await self.get_selected_user(inter)
        await auth.set_active_arknights_account(arknights_user)

        await inter.response.edit_message(
            localisation.localise("auth_ak_set_active_success", inter.locale),
            components=None,
        )


@manager.register(identifier="ArkDelete")
class ArknightsRemoveAccountSelect(component_base.ArknightsAccountSelect):
    """Select menu to remove a user's Arknights account from the bot."""

    async def callback(self, inter: components.MessageInteraction) -> None:
        """Select an Arknights account to unlink."""
        arknights_user = await self.get_selected_user(inter)
        duffelbag_user = await auth.get_user_by_platform(
            platform=auth.Platform.DISCORD,
            platform_id=inter.author.id,
            strict=True,
        )

        scheduled_deletion = await auth.schedule_arknights_user_deletion(
            duffelbag_user,
            arknights_user,
        )

        schedule_user_deletion(scheduled_deletion)

        await inter.response.edit_message(
            localisation.localise(
                "auth_ak_remove_schedule",
                locale=inter.locale,
                format_map={"timestamp": scheduled_deletion.deletion_ts},
            ),
            components=None,
        )


@account_.error  # pyright: ignore
async def account_error_handler(
    inter: disnake.Interaction,
    exception: Exception,
) -> typing.Literal[True]:
    """Handle any kind of authentication exception."""
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

        case exceptions.LoginError(account_type="Duffelbag"):
            key = "exc_auth_dfb_loginfail"

        case exceptions.LoginError(account_type="Platform"):
            key = "exc_auth_pf_loginfail"
            params["platform"] = auth.Platform.DISCORD.value

        case exceptions.LoginError(account_type="Arknights"):
            key = "exc_auth_ak_loginfail"

        case exceptions.PlatformConnectionExistsError(is_own=is_own):
            key = "exc_auth_pf_exists_self" if is_own else "exc_auth_pf_exists"
            params["platform"] = auth.Platform.DISCORD.value

        case exceptions.ArknightsConnectionExistsError(is_own=is_own):
            key = "exc_auth_ak_exists_self" if is_own else "exc_auth_ak_exists"

        case exceptions.DuffelbagDeletionAlreadyQueuedError():
            key = "exc_auth_dfb_remove_exists"
            params["timestamp"] = disnake.utils.format_dt(exception.deletion_ts, "R")

        case exceptions.ArknightsDeletionAlreadyQueuedError():
            key = "exc_auth_ak_remove_exists"
            params["timestamp"] = disnake.utils.format_dt(exception.deletion_ts, "R")

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


@manager.as_exception_handler
async def handle_component_exception(
    _manager: components.ComponentManager,
    _component: components.api.RichComponent,
    inter: disnake.Interaction,
    exception: Exception,
) -> bool:
    """Handle auth component exceptions.

    This passes exceptions to the above exception handler.
    """
    try:
        return await account_error_handler(inter, exception)
    except Exception:  # noqa: BLE001
        return False


# User deletion task scheduling.


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


async def _delayed_arknights_user_deletion(
    scheduled_deletion: database.ScheduledArknightsUserDeletion,
) -> None:
    timedelta = scheduled_deletion.deletion_ts - datetime.datetime.now(tz=datetime.UTC)
    await asyncio.sleep(timedelta.total_seconds())

    duffelbag_user, arknights_user = await auth.get_scheduled_arknights_user_deletion_users(
        scheduled_deletion,
    )
    accounts = await auth.list_connected_accounts(duffelbag_user, platform=auth.Platform.DISCORD)

    guest_client = shared.get_guest_client()
    arknights_account = (
        await guest_client.get_partial_players(
            [arknights_user.game_uid],
            server=typing.cast(arkprts.ArknightsServer, arknights_user.server),
        )
    )[0]
    display_name = f"{arknights_account.nickname}#{arknights_account.nick_number}"

    for account in accounts:
        try:
            user = await plugin.bot.get_or_fetch_user(account.platform_id, strict=True)
            await user.send(
                localisation.localise(
                    "auth_ak_remove_success",
                    disnake.Locale.en_GB,  # TODO: figure out some way of getting locale information
                    format_map={"username": display_name},
                ),
            )

        except disnake.HTTPException:
            _LOGGER.warning(
                "Failed to notify Discord user with id %i of their Arknights account deletion.",
                account.platform_id,
            )

    await arknights_user.remove()


def schedule_user_deletion(
    scheduled_deletion: database.ScheduledUserDeletion | database.ScheduledArknightsUserDeletion,
) -> None:
    """Create a user deletion background task for a provided ScheduledUserDeletion."""
    if isinstance(scheduled_deletion, database.ScheduledUserDeletion):
        async_utils.safe_task(_delayed_user_deletion(scheduled_deletion))

    else:
        async_utils.safe_task(_delayed_arknights_user_deletion(scheduled_deletion))


@plugin.load_hook()
async def schedule_user_deletions() -> None:
    """Get scheduled user deletions and create tasks for them."""
    for scheduled_deletion in await auth.get_scheduled_user_deletions():
        schedule_user_deletion(scheduled_deletion)

    for scheduled_deletion in await auth.get_scheduled_arknights_user_deletions():
        schedule_user_deletion(scheduled_deletion)


setup, teardown = plugin.create_extension_handlers()

"""Bot plugin for Discord <-> Arknights user authentication."""

import asyncio
import datetime
import re
import typing

import arkprts
import hikari
import hikari.errors
import hikari.interactions.modal_interactions
import ryoshu
import tanjun

import database
from duffelbag import async_utils, auth, exceptions, log, shared
from duffelbag.discord import component_base, localisation

_LOGGER = log.get_logger(__name__)
_EMAIL_REGEX: typing.Final[typing.Pattern[str]] = re.compile(
    # https://stackoverflow.com/a/201378
    r"^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$",
)


component = tanjun.Component(name=__name__)
manager = ryoshu.get_manager("duffelbag.auth")
root_manager = ryoshu.get_manager()


# Account manipulation commands.


account_group = component.with_slash_command(tanjun.slash_command_group("account", "Do stuff with accounts."))
account_duffelbag_group = account_group.make_sub_group("duffelbag", "Do stuff with Duffelbag accounts.")
account_discord_group = account_group.make_sub_group("discord", "Do stuff with Discord accounts.")
account_arknights_group = account_group.make_sub_group("arknights", "Do stuff with Arknights accounts.")


_USER_DESC = (
    f"The username to use. Must be between {auth.MIN_USER_LEN} and"
    f" {auth.MAX_USER_LEN} characters long."
)
_PASS_DESC = (
    f"The password to use. Must be between {auth.MIN_PASS_LEN} and"
    f" {auth.MAX_PASS_LEN} characters long."
)


@component.with_slash_command
@tanjun.with_str_slash_option("password", _PASS_DESC, min_length=auth.MIN_PASS_LEN, max_length=auth.MAX_PASS_LEN)
@tanjun.with_str_slash_option("username", _USER_DESC, min_length=auth.MIN_USER_LEN, max_length=auth.MAX_USER_LEN)
@account_duffelbag_group.as_sub_command("create", "Create a new Duffelbag account and bind your discord account to it.")
async def account_duffelbag_create(
    ctx: tanjun.abc.SlashContext,
    username: str,
    password: str,
) -> None:
    """Create a new Duffelbag account and bind your discord account to it."""
    await auth.create_user(
        username=username,
        password=password,
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
    )

    await ctx.create_initial_response(
        localisation.localise(
            "auth_new_collapsed",
            ctx.interaction.locale,
            format_map={"username": username},
        ),
        component=await ryoshu.into_action_row(
            root_manager.make_button(
                "ExpBtn",
                key_base="auth_new",
                params=[username, auth.Platform.DISCORD.value],
            ),
        ),
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@component.with_slash_command
@tanjun.with_str_slash_option("password", _PASS_DESC, min_length=auth.MIN_PASS_LEN, max_length=auth.MAX_PASS_LEN)
@account_duffelbag_group.as_sub_command(
    "recover",
    "Recover the Duffelbag account connected to your discord account by setting a new password.",
)
async def account_duffelbag_recover(
    ctx: tanjun.abc.SlashContext,
    password: str,
) -> None:
    """Recover the Duffelbag account connected to your discord account by setting a new password."""
    duffelbag_user = await auth.recover_user(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
        password=password,
    )

    await ctx.create_initial_response(
        localisation.localise(
            "auth_recover",
            ctx.interaction.locale,
            format_map={"username": duffelbag_user.username, "password": password},
        ),
        ephemeral=True,
    )


@component.with_slash_command
@tanjun.with_str_slash_option("password", _PASS_DESC, min_length=auth.MIN_PASS_LEN, max_length=auth.MAX_PASS_LEN)
@account_duffelbag_group.as_sub_command("delete", "Delete your duffelbag account. This has a 24 hour grace period.")
async def account_duffelbag_delete(
    ctx: tanjun.abc.SlashContext,
    password: str,
) -> None:
    """Delete your duffelbag account. This has a 24 hour grace period."""
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
        strict=True,
    )

    auth.verify_password(duffelbag_user=duffelbag_user, password=password)

    scheduled_deletion = await auth.schedule_user_deletion(duffelbag_user)
    schedule_user_deletion(scheduled_deletion)

    await ctx.create_initial_response(
        localisation.localise(
            "auth_delete_schedule",
            ctx.interaction.locale,
            format_map={
                "timestamp": localisation.format_timestamp(scheduled_deletion.deletion_ts, style="R"),
            },
        ),
        ephemeral=True,
    )


@component.with_slash_command
@tanjun.with_str_slash_option("password", _PASS_DESC, min_length=auth.MIN_PASS_LEN, max_length=auth.MAX_PASS_LEN)
@tanjun.with_str_slash_option("username", _USER_DESC, min_length=auth.MIN_USER_LEN, max_length=auth.MAX_USER_LEN)
@account_discord_group.as_sub_command("bind", "Bind your Discord account to an existing Duffelbag account.")
async def account_discord_bind(
    ctx: tanjun.abc.SlashContext,
    username: str,
    password: str,
) -> None:
    """Bind your Discord account to an existing Duffelbag account."""
    duffelbag_user = await auth.login_user(username=username, password=password)

    await auth.add_platform_account(
        duffelbag_user,
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
    )

    await ctx.create_initial_response(
        localisation.localise(
            "auth_bind_platform",
            locale=ctx.interaction.locale,
            format_map={
                "platform": auth.Platform.DISCORD.value,
                "username": username,
            },
        ),
        ephemeral=True,
    )

@component.with_slash_command
@tanjun.with_str_slash_option(
    "server",
    "The server to which your Arknights account is registered.",
    min_length=2,
    max_length=4,
    choices=["en", "jp", "kr", "cn", "bili", "tw"],
)
@tanjun.with_str_slash_option("email", "The email address bound to your Arknights account.")
@account_arknights_group.as_sub_command("bind", "Bind an Arknights account to your Duffelbag account.")
async def account_arknights_bind(
    ctx: tanjun.abc.SlashContext,
    server: arkprts.ArknightsServer,
    email: str,
) -> None:
    """Bind an Arknights account to your Duffelbag account."""
    await ctx.defer(ephemeral=True)

    if not _EMAIL_REGEX.fullmatch(email):
        msg = f"The provided email address {email!r} is not a valid email address."
        raise exceptions.InvalidEmailError(msg, email=email)

    await auth.start_authentication(server=server, email=email)

    button = ArknightsBindButton(
        label=localisation.localise("auth_bind_ak_title", locale=ctx.interaction.locale),
        server=server,
        email=email,
    )

    await ctx.edit_last_response(
        localisation.localise(
            "auth_bind_ak",
            locale=ctx.interaction.locale,
            format_map={"email": email},
        ),
        component=await ryoshu.into_action_row(button),
    )


@component.with_slash_command
@account_arknights_group.as_sub_command("set-active", "Set a different Arknights account as your active account.")
async def account_arknights_set_active(ctx: tanjun.abc.SlashContext) -> None:
    """Set a different Arknights account as your active account."""
    await ctx.defer(ephemeral=True)

    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
        strict=True,
    )
    component = await ArknightsActiveAccountSelect.for_duffelbag_user(duffelbag_user)

    await ctx.edit_last_response(
        localisation.localise("auth_ak_set_active", ctx.interaction.locale),
        component=await ryoshu.into_action_row(component),
    )


@component.with_slash_command
@tanjun.with_str_slash_option("password", _PASS_DESC, min_length=auth.MIN_PASS_LEN, max_length=auth.MAX_PASS_LEN)
@account_arknights_group.as_sub_command("set-active", "Set a different Arknights account as your active account.")
async def account_arknights_unbind(
    ctx: tanjun.abc.SlashContext,
    password: str,
) -> None:
    """Unlink your Arknights account. This has a 24 hour grace period."""
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
        strict=True,
    )

    auth.verify_password(duffelbag_user=duffelbag_user, password=password)

    component = await ArknightsRemoveAccountSelect.for_duffelbag_user(duffelbag_user)

    await ctx.create_initial_response(
        localisation.localise("auth_ak_remove_msg", ctx.interaction.locale),
        component=await ryoshu.into_action_row(component),
        ephemeral=True,
    )


# Account manipulation components.


@manager.register(identifier="ArkBind")
class ArknightsBindButton(ryoshu.ManagedButton):
    """Button to complete the Arknights account verification process."""

    style: hikari.ButtonStyle | int = hikari.ButtonStyle.SUCCESS

    server: arkprts.ArknightsServer = ryoshu.field(
        parser=ryoshu.parser.StringParser,  # pyright: ignore  # TODO: implement literal parser
    )
    email: str

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:
        """Verify and link an Arknights account to a Duffelbag account."""
        assert isinstance(event.interaction, hikari.ComponentInteraction)

        locale = event.interaction.locale
        custom_id = f"arknights_verify|{event.interaction.id}"
        action_row = (
            hikari.impl.ModalActionRowBuilder()
            .add_text_input(
                "verification_code",
                localisation.localise("auth_bind_ak_modal_label", locale),
                min_length=6,
                max_length=6,
                placeholder="XXXXXX",
            )
        )
        await event.interaction.create_modal_response(
            title=self.label or "UNKNOWN",
            custom_id=custom_id,
            component=action_row,
        )

        assert isinstance(event.app, hikari.GatewayBot)  # TODO: DI bot into here?
        # NOTE: asyncio.TimeoutError is handled by the component manager.
        modal_event: hikari.InteractionCreateEvent = await event.app.wait_for(
            hikari.InteractionCreateEvent,
            predicate=lambda event: (
                isinstance(event.interaction, hikari.ModalInteraction)
                and event.interaction.custom_id == custom_id
            ),
            timeout=5 * 60,
        )

        assert isinstance(modal_event.interaction, hikari.ModalInteraction)
        await modal_event.interaction.create_initial_response(
            response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
            flags=hikari.MessageFlag.EPHEMERAL,
        )

        # There's only one row with one component, so we can select it as such.
        component = modal_event.interaction.components[0][0]
        assert isinstance(component, hikari.TextInputComponent)
        verification_code = component.value

        if not verification_code.isdigit():
            await modal_event.interaction.edit_initial_response(
                localisation.localise(
                    "auth_bind_ak_invalid_vcode",
                    locale=locale,
                    format_map={"code": verification_code},
                ),
            )
            return

        duffelbag_user = await auth.get_user_by_platform(
            platform=auth.Platform.DISCORD,
            platform_id=event.interaction.user.id,
            strict=True,
        )

        arknights_user = await auth.complete_authentication(
            duffelbag_user,
            server=self.server,
            email=self.email,
            verification_code=verification_code,
        )

        await modal_event.interaction.edit_initial_response(
            localisation.localise(
                "auth_bind_ak_success_active" if arknights_user.active else "auth_bind_ak_success",
                locale=locale,
            ),
        )


@manager.register(identifier="ArkActive")
class ArknightsActiveAccountSelect(component_base.ArknightsAccountSelect):
    """Select menu to set a user's active Arknights account."""

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:
        """Select an Arknights account to mark as active."""
        assert isinstance(event.interaction, hikari.ComponentInteraction)

        arknights_user = await self.get_selected_user(event.interaction)
        await auth.set_active_arknights_account(arknights_user)

        await event.interaction.create_initial_response(
            response_type=hikari.ResponseType.MESSAGE_UPDATE,
            content=localisation.localise("auth_ak_set_active_success", event.interaction.locale),
            components=None,
        )


@manager.register(identifier="ArkDelete")
class ArknightsRemoveAccountSelect(component_base.ArknightsAccountSelect):
    """Select menu to remove a user's Arknights account from the bot."""

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:
        """Select an Arknights account to unlink."""
        assert isinstance(event.interaction, hikari.ComponentInteraction)

        arknights_user = await self.get_selected_user(event.interaction)
        duffelbag_user = await auth.get_user_by_platform(
            platform=auth.Platform.DISCORD,
            platform_id=event.interaction.user.id,
            strict=True,
        )

        scheduled_deletion = await auth.schedule_arknights_user_deletion(
            duffelbag_user,
            arknights_user,
        )

        schedule_user_deletion(scheduled_deletion)

        await event.interaction.create_initial_response(
            response_type=hikari.ResponseType.MESSAGE_UPDATE,
            content=localisation.localise(
                "auth_ak_remove_schedule",
                locale=event.interaction.locale,
                format_map={"timestamp": scheduled_deletion.deletion_ts},
            ),
            components=None,
        )


hooks = tanjun.AnyHooks()
component.set_slash_hooks(hooks)


@hooks.with_on_error
async def account_error_handler(  # noqa: C901
    ctx: tanjun.abc.SlashContext,
    exception: Exception,
) -> typing.Literal[True]:
    """Handle any kind of authentication exception."""
    _LOGGER.trace(
        "Handling auth exception of type %r for user %r.",
        type(exception).__name__,
        ctx.author.id,
    )

    params: dict[str, object] = {}
    msg_components: list[ryoshu.api.ManagedComponent] = []

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
            params["timestamp"] = localisation.format_timestamp(exception.deletion_ts, "R")

        case exceptions.ArknightsDeletionAlreadyQueuedError():
            key = "exc_auth_ak_remove_exists"
            params["timestamp"] = localisation.format_timestamp(exception.deletion_ts, "R")

        case _:
            _LOGGER.trace("Exception went unhandled in local error handler.")
            raise exception

    params |= exception.to_dict()

    await ctx.create_initial_response(
        localisation.localise(key, ctx.interaction.locale, format_map=params),
        component=await ryoshu.into_action_row(*msg_components) if msg_components else hikari.UNDEFINED,
        ephemeral=True,
    )

    _LOGGER.trace("Exception handled successfully in local error handler.")
    return True


@manager.as_exception_handler
async def handle_component_exception(
    _manager: ryoshu.ComponentManager,
    _component: ryoshu.api.ManagedComponent,
    event: hikari.InteractionCreateEvent,
    exception: Exception,
) -> bool:
    """Handle auth component exceptions.

    This passes exceptions to the above exception handler.
    """
    try:
        # TODO: make this work somehow.
        return await account_error_handler(event, exception)  # pyright: ignore
    except Exception:  # noqa: BLE001
        return False


# User deletion task scheduling.


async def _delayed_user_deletion(scheduled_deletion: database.ScheduledUserDeletion) -> None:
    assert component.client
    assert component.client.cache

    timedelta = scheduled_deletion.deletion_ts - datetime.datetime.now(tz=datetime.UTC)
    await asyncio.sleep(timedelta.total_seconds())

    duffelbag_user = await auth.get_scheduled_user_deletion_user(scheduled_deletion)
    accounts = await auth.list_connected_accounts(duffelbag_user, platform=auth.Platform.DISCORD)

    for account in accounts:
        try:
            user = (
                component.client.cache.get_user(account.platform_id)
                or await component.client.rest.fetch_user(account.platform_id)
            )
            await user.send(
                localisation.localise(
                    "auth_delete_success",
                    "en-GB",  # TODO: figure out some way of getting locale information
                    format_map={"username": duffelbag_user.username},
                ),
            )

        except hikari.ForbiddenError:
            _LOGGER.warning(
                "Failed to notify Discord user with id %i of their Duffelbag account deletion.",
                account.platform_id,
            )

    await duffelbag_user.remove()


async def _delayed_arknights_user_deletion(
    scheduled_deletion: database.ScheduledArknightsUserDeletion,
) -> None:
    assert component.client
    assert component.client.cache

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
            user = (
                component.client.cache.get_user(account.platform_id)
                or await component.client.rest.fetch_user(account.platform_id)
            )
            await user.send(
                localisation.localise(
                    "auth_ak_remove_success",
                    "en-GB",  # TODO: figure out some way of getting locale information
                    format_map={"username": display_name},
                ),
            )

        except hikari.ForbiddenError:
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


@component.with_client_callback(tanjun.ClientCallbackNames.STARTING)
async def schedule_user_deletions() -> None:
    """Get scheduled user deletions and create tasks for them."""
    for scheduled_deletion in await auth.get_scheduled_user_deletions():
        async_utils.safe_task(_delayed_user_deletion(scheduled_deletion))

    for scheduled_deletion in await auth.get_scheduled_arknights_user_deletions():
        async_utils.safe_task(_delayed_arknights_user_deletion(scheduled_deletion))


loader = component.make_loader()

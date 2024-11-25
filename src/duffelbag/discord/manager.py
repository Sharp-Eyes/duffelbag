"""Utilities for ryoshu."""

import asyncio
import typing

import hikari
import ryoshu
import tanjun

from duffelbag import log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)


async def log_callback_result(
    manager: ryoshu.ComponentManager,
    component: ryoshu.api.ManagedComponent,
    _event: hikari.InteractionCreateEvent,
) -> typing.AsyncGenerator[None, None]:
    """Log the callback result for *all* component interactions."""
    try:
        # Run component callback...
        _LOGGER.trace("Running component %r on manager %r.", type(component).__name__, manager.name)
        yield

    except Exception:
        # NOTE: We could've used an exception handler for this, but ultimately
        #       it's just nicer to have this all in one callback. Functionally,
        #       there is no difference.

        # Log any exception...
        # NOTE: Exception info does not need to be logged as the standard
        #       exception handler on the root manager does this anyways.
        _LOGGER.exception(
            "An exception occurred while handling the callback for component %r:",
            manager.make_identifier(type(component)),
        )
        raise

    else:
        # Log success...
        _LOGGER.info(
            "Successfully invoked the callback component %r.",
            manager.make_identifier(type(component)),
        )


async def handle_component_exception(
    _manager: ryoshu.ComponentManager,
    _component: ryoshu.api.ManagedComponent,
    event: hikari.InteractionCreateEvent,
    exception: Exception,
) -> bool:
    """Handle component exceptions by notifying the user and logging them."""
    assert isinstance(event.interaction, hikari.ComponentInteraction)
    params = {}

    match exception:
        case asyncio.TimeoutError():
            key = "component_timeout"

        case _:
            key = "general_component_err"

    # We intentionally use inter.send here as we don't know whether or not the
    # interaction has been responded to before.
    await event.interaction.create_initial_response(
        response_type=hikari.ResponseType.MESSAGE_CREATE,
        content=localisation.localise(key, event.interaction.locale, format_map=params),
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    # Let the default manager implementation log the exception.
    return False


async def component_perms(
    manager: ryoshu.ComponentManager,
    component: ryoshu.api.ManagedComponent,
    event: hikari.InteractionCreateEvent,
) -> typing.AsyncGenerator[None, None]:
    """Check permissions for ryoshu on this manager."""
    interaction = event.interaction

    if not isinstance(interaction, hikari.ComponentInteraction):
        msg = f"Manager {manager.name!r} only supports message interactions."
        raise TypeError(msg)

    _LOGGER.trace(
        "Checking permissions for user %r w.r.t. component %r.",
        interaction.user.id,
        type(component).__name__,
    )

    source_interaction = interaction.message.interaction

    if not source_interaction:
        # The message wasn't sent by a slash command, so we can't do automatic
        # ownership checks. We just invoke the component, either the component
        # handles the ownership check or it intentionally doesn't check for
        # ownership.
        # (In reality, this won't ever happen as we only use slash commands)
        _LOGGER.trace("Skipping permissions check.")
        yield
        return

    guild = interaction.get_guild()
    if guild:  # Ensure we're in a guild.
        channel = interaction.get_channel()
        assert channel
        assert interaction.member

        permissions = tanjun.permissions.calculate_permissions(interaction.member, guild, guild.get_roles())

        if not (
            source_interaction.user != interaction
            or permissions & hikari.Permissions.MANAGE_MESSAGES
        ):
            _LOGGER.trace("Permissions check failed.")

            # TODO: Custom exception!
            msg = "You are not allowed to use this component!"
            raise RuntimeError(msg)

    _LOGGER.trace("Permissions check succeeded.")
    yield


def initialise() -> None:
    """Initialise component managers."""
    duffelbag_manager = ryoshu.get_manager("duffelbag")
    duffelbag_manager.as_callback_wrapper(log_callback_result)
    duffelbag_manager.as_exception_handler(handle_component_exception)

    restricted_manager = ryoshu.get_manager("duffelbag.restricted")
    restricted_manager.as_callback_wrapper(component_perms)

    _LOGGER.trace("Successfully initialised component managers.")

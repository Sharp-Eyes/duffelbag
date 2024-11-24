"""Utilities for components."""

import asyncio
import typing

import disnake
from disnake.ext import components

from duffelbag import log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)


async def log_callback_result(
    manager: components.ComponentManager,
    component: components.api.RichComponent,
    _inter: disnake.Interaction,
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
    _manager: components.ComponentManager,
    _component: components.api.RichComponent,
    inter: disnake.Interaction,
    exception: Exception,
) -> bool:
    """Handle component exceptions by notifying the user and logging them."""
    params = {}

    match exception:
        case asyncio.TimeoutError():
            key = "component_timeout"

        case _:
            key = "general_component_err"

    # We intentionally use inter.send here as we don't know whether or not the
    # interaction has been responded to before.
    await inter.send(
        localisation.localise(key, inter.locale, format_map=params),
        ephemeral=True,
    )

    # Let the default manager implementation log the exception.
    return False


async def component_perms(
    manager: components.ComponentManager,
    component: components.api.RichComponent,
    inter: disnake.Interaction,
) -> typing.AsyncGenerator[None, None]:
    """Check permissions for components on this manager."""
    _LOGGER.trace(
        "Checking permissions for user %r w.r.t. component %r.",
        inter.author.id,
        type(component).__name__,
    )

    if not isinstance(inter, disnake.MessageInteraction):
        msg = f"Manager {manager.name!r} only supports message interactions."
        raise TypeError(msg)

    source_interaction = inter.message.interaction

    if not source_interaction:
        # The message wasn't sent by a slash command, so we can't do automatic
        # ownership checks. We just invoke the component, either the component
        # handles the ownership check or it intentionally doesn't check for
        # ownership.
        # (In reality, this won't ever happen as we only use slash commands)
        _LOGGER.trace("Skipping permissions check.")
        yield
        return

    if (
        inter.guild  # Bypass permission checks in DMs,
        and isinstance(inter.author, disnake.Member)  # Member assertion, as we're not in DMs,
        and source_interaction.author != inter.author  # Allow only the original command author,
        and not inter.author.guild_permissions.manage_messages  # Allow anyone with manage_messages permissions,  # noqa: E501
    ):
        _LOGGER.trace("Permissions check failed.")

        # TODO: Custom exception!
        msg = "You are not allowed to use this component!"
        raise RuntimeError(msg)

    _LOGGER.trace("Permissions check succeeded.")
    yield


def initialise() -> None:
    """Initialise component managers."""
    duffelbag_manager = components.get_manager("duffelbag")
    duffelbag_manager.as_callback_wrapper(log_callback_result)
    duffelbag_manager.as_exception_handler(handle_component_exception)

    restricted_manager = components.get_manager("duffelbag.restricted")
    restricted_manager.as_callback_wrapper(component_perms)

    _LOGGER.trace("Successfully initialised component managers.")

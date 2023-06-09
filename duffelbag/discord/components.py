"""Utilities for components."""

import typing

import disnake
from disnake.ext import components

from duffelbag import log

_LOGGER = log.get_logger(__name__)


root_manager = components.get_manager()


@root_manager.as_callback_wrapper
async def log_callback_result(
    manager: components.ComponentManager,
    component: components.api.RichComponent,
    _: disnake.Interaction,
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


restricted_manager = components.get_manager("duffelbag.restricted")


@restricted_manager.as_callback_wrapper
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

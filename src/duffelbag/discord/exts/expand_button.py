"""Extension module for a button that can expand/collapse text."""

import typing

import hikari
import ryoshu
import tanjun

from duffelbag import log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)


class _ExpandButtonParams(typing.NamedTuple):
    label: str
    emoji: str
    key_suffix: str


_EXPAND: typing.Final = _ExpandButtonParams(
    "Expand...",
    "<:expand:1113954208014684252>",
    "_collapsed",
)
_COLLAPSE: typing.Final = _ExpandButtonParams(
    "Collapse...",
    "<:collapse:1113954205766537226>",
    "_expanded",
)

component = tanjun.Component(name="expand_button")

# NOTE: This manager has ownership/permissions checks, see
#       'duffelbag.discord.components.restricted_manager'
manager = ryoshu.get_manager("duffelbag.restricted")


class _PosToFormatMap(dict[str, object]):
    # HACK: dict that returns positional items when __getitem__'d, such that
    #       str.format_map can take positional arguments. This is done so that
    #       we don't need to store localisation string format keys in the
    #       custom id, and can instead provide the parameters positionally.

    def __init__(self, args: typing.Iterable[object], *, strict: bool) -> None:
        self._arg_iter = iter(args)
        self.strict = strict

        super().__init__()

    def __missing__(self, key: str) -> object:
        value = next(self._arg_iter) if self.strict else next(self._arg_iter, f"{{{key}}}")
        self[key] = value
        return value


@manager.register(identifier="ExpBtn")
class ExpandButton(ryoshu.ManagedButton):
    """A button that toggles a message between expanded and collapsed state."""

    # Start collapsed, so show expand label and emoji.
    label: str | None = _EXPAND.label
    emoji: hikari.Snowflakeish | hikari.Emoji | str | None = _EXPAND[1]

    # Custom id params:
    key_base: str
    params: list[str]
    collapsed: bool = True

    def _format(self, string: str) -> str:
        return string.format_map(_PosToFormatMap(self.params, strict=True))

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:
        """Toggle between expanded/collapsed."""
        interaction = event.interaction
        assert isinstance(interaction, hikari.ComponentInteraction)

        self.collapsed ^= True
        _LOGGER.trace(
            "Toggling expand button state for user %r to %r.",
            interaction.user.display_name,
            "collapsed" if self.collapsed else "expanded",
        )

        self.label, self.emoji, key_suffix = _EXPAND if self.collapsed else _COLLAPSE

        # NOTE: strict=False is required here as we need to format with
        #       self.params after localisation formatting is done. Since we
        #       call str.format_map on the result again later anyways, there's
        #       no risk of unformatted keys appearing in the output, either.
        message = localisation.localise(self.key_base + key_suffix, interaction.locale, strict=False)

        message_components, _ = await manager.parse_message_components(interaction.message)
        await interaction.create_initial_response(
            response_type=hikari.ResponseType.MESSAGE_UPDATE,
            content=self._format(message),
            components=await ryoshu.into_action_rows(message_components),
        )


loader = component.make_loader()

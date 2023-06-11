"""Extension module for a button that can expand/collapse text."""

import typing

import disnake
from disnake.ext import components, plugins

from duffelbag import log
from duffelbag.discord import localisation

_LOGGER = log.get_logger(__name__)

_EXPAND: typing.Final[tuple[str, str, str]] = (
    "Expand...",
    "<:expand:1113954208014684252>",
    "_collapsed",
)
_COLLAPSE: typing.Final[tuple[str, str, str]] = (
    "Collapse...",
    "<:collapse:1113954205766537226>",
    "_expanded",
)

plugin = plugins.Plugin()

# NOTE: This manager has ownership/permissions checks, see
#       'duffelbag.discord.components.restricted_manager'
manager = components.get_manager("duffelbag.restricted")


class _StringListParser(components.Parser[list[str]]):
    # TODO: Implement list support into ext-components :trol:

    def loads(self, _: disnake.Interaction, arg: str) -> list[str]:
        return arg.split(",")

    def dumps(self, arg: list[str]) -> str:
        return ",".join(arg)


class _PosToFormatMap(dict[str, object]):
    # HACK: dict that returns positional items when __getitem__'d, such that
    #       str.format_map can take positional arguments. This is done so that
    #       we don't need to store localisation string format keys in the
    #       custom id, and can instead provide the parameters positionally.

    def __init__(self, *args: object, strict: bool = True) -> None:
        self._arg_iter = iter(args)
        self.strict = strict

        super().__init__()

    def __missing__(self, key: str) -> object:
        value = next(self._arg_iter) if self.strict else next(self._arg_iter, f"{{{key}}}")
        self[key] = value
        return value


@manager.register(identifier="ExpBut")
class ExpandButton(components.RichButton):
    """A button that toggles a message between expanded and collapsed state."""

    # Start collapsed, so show expand label and emoji.
    label: str = _EXPAND[0]
    emoji: str = _EXPAND[1]

    # Custom id params:
    key_base: str
    params: list[str] = components.field(parser=_StringListParser())
    collapsed: bool = True

    def _format(self, string: str) -> str:
        return string.format_map(_PosToFormatMap(*self.params))

    async def callback(self, inter: components.MessageInteraction) -> None:
        """Toggle between expanded/collapsed."""
        self.collapsed ^= True
        _LOGGER.trace(
            "Toggling expand button state for user %r to %r.",
            inter.author.name,
            "collapsed" if self.collapsed else "expanded",
        )

        self.label, self.emoji, key_ext = _EXPAND if self.collapsed else _COLLAPSE

        # NOTE: strict=False is required here as we need to format with
        #       self.params after localisation formatting is done. Since we
        #       call str.format_map on the result again later anyways, there's
        #       no risk of unformatted keys appearing in the output, either.
        message = localisation.localise(self.key_base + key_ext, inter.locale, strict=False)

        # TODO: Don't just consume existing components.
        await inter.response.edit_message(self._format(message), components=self)


setup, teardown = plugin.create_extension_handlers()

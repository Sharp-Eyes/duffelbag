"""Module for Duffelbag eval command.

Note that eval requires messages/guild_messages intents, and therefore only
works when the env var `DISCORD_IS_PROD` is set to false.
"""

import ast
import asyncio
import contextlib
import inspect
import io
import linecache
import os
import re
import sys
import textwrap
import traceback
import typing

import disnake
from disnake.ext import commands, plugins

import database
from duffelbag.discord import config

if typing.TYPE_CHECKING:
    import types

_valid_ids: set[int] = set()

plugin = plugins.Plugin()


# Credit to Monty-Python eval
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"  # code delimiter: 1-3 backticks;
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"  # if we're in a block, match optional language
    r"(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all code inside the markup
    r"\s*"  # any more whitespace before the end of the code markup
    r"(?P=delim)",  # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE,  # "." also matches newlines, case insensitive
)


def _clean_code(raw_code: str) -> tuple[str, str]:
    if match := list(FORMATTED_CODE_REGEX.finditer(raw_code)):
        blocks = [block for block in match if block.group("block")]

        if len(blocks) > 1:
            code = "\n".join(block.group("code") for block in blocks)
            lang = blocks[0].group("lang")
        else:
            match = blocks[0] if blocks else match[0]
            code, lang = match.group("code", "lang")

    else:
        msg = "Encountered invalid code block."
        raise RuntimeError(msg)

    return textwrap.dedent(code), lang


async def _eval_py(code: str, env: dict[str, object]) -> str:
    sio = io.StringIO()
    try:
        compiled: types.CodeType = compile(
            code,
            "<eval>",
            "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )

        # This enables 3.11-style error reporting (arrows pointing to error location etc.)
        linecache.cache[compiled.co_filename] = (
            len(code),
            None,
            code.splitlines(keepends=True),
            compiled.co_filename,
        )

        with contextlib.redirect_stdout(sio):
            result = exec(compiled, env)  # noqa: S102
            if inspect.isawaitable(result):
                result = await result

    except Exception:  # noqa: BLE001
        error = traceback.format_exception(*sys.exc_info())
        error.pop(1)  # Pop the traceback entry pointing to the exec statement above.
        return "".join(error)

    else:
        return sio.getvalue().strip()


@plugin.listener("on_message")
async def eval_listener(message: disnake.Message) -> None:
    """Evaluate codeblock(s) in a message."""
    if message.author.id not in _valid_ids:
        return

    content = message.content.strip()
    if not content.startswith(f"{plugin.bot.user.mention} eval"):
        return

    code, lang = _clean_code(message.content)
    if lang in ("py", "python"):
        env: dict[str, object] = {
            "bot": plugin.bot,
            "channel": message.channel,
            "author": message.author,
            "guild": message.guild,
            "message": message,
            "asyncio": asyncio,
            "io": io,
            "os": os,
            "sys": sys,
            "typing": typing,
            "disnake": disnake,
            "commands": commands,
            "database": database,
        }

        out = await _eval_py(code, env)

    else:
        msg = "Postgres soontm"
        raise NotImplementedError(msg)

    await message.channel.send(f"```\n{out}\n```")


@plugin.load_hook()
async def populate_eval_users() -> None:
    """Populate set of users that are allowed to use eval."""
    owner_ids = {plugin.bot.owner_id} if plugin.bot.owner_id else plugin.bot.owner_ids

    _valid_ids.update(config.BOT_CONFIG.SUPERUSER_IDS, owner_ids)


setup, teardown = plugin.create_extension_handlers()

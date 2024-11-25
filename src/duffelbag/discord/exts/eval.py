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
import types
import typing

import hikari
import ryoshu
import tanjun

import database
from duffelbag.discord import config

_valid_ids: set[int] = set()

component = tanjun.Component(name="eval")


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
            f = types.FunctionType(compiled, env)
            result = f()
            if inspect.isawaitable(result):
                result = await result

    except Exception:  # noqa: BLE001
        error = traceback.format_exception(*sys.exc_info())
        error.pop(1)  # Pop the traceback entry pointing to the exec statement above.
        return "".join(error)

    else:
        return sio.getvalue().strip()


@component.with_listener()
async def eval_listener(event: hikari.MessageCreateEvent) -> None:
    """Evaluate codeblock(s) in a message."""
    assert component.client

    message = event.message
    if not message.content:
        return

    if message.author.id not in _valid_ids:
        return

    content = message.content.strip()
    if not content.startswith("<@1064181759278858280> eval"):  # TODO: Make mention dynamically
        return

    code, lang = _clean_code(message.content)
    if lang in ("py", "python"):
        env: dict[str, object] = {
            "bot": component.client,
            "author": message.author,
            "message": message,
            "asyncio": asyncio,
            "io": io,
            "os": os,
            "sys": sys,
            "typing": typing,
            "hikari": hikari,
            "tanjun": tanjun,
            "ryoshu": ryoshu,
            "database": database,
            "channel": None,
            "guild": None,
        }

        if component.client.cache:
            env["channel"] = component.client.cache.get_guild_channel(message.channel_id)
            if message.guild_id:
                env["guild"] = component.client.cache.get_guild(message.guild_id)


        out = await _eval_py(code, env)

    else:
        msg = "Postgres soontm"
        raise NotImplementedError(msg)

    await message.respond(f"```\n{out}\n```")


@component.with_client_callback(tanjun.ClientCallbackNames.STARTED)
async def populate_eval_users() -> None:
    """Populate set of users that are allowed to use eval."""
    # owner_ids = {component.client.} if plugin.bot.owner_id else plugin.bot.owner_ids
    owner_ids = set()

    _valid_ids.update(config.BOT_CONFIG.SUPERUSER_IDS, owner_ids)


loader = component.make_loader()

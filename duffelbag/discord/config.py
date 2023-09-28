"""Discord bot configuration from .env file."""

import os
import typing

import dotenv
import pydantic
import typing_extensions

__all__: typing.Sequence[str] = ("BOT_CONFIG",)

dotenv.load_dotenv()


def _to_list(inp: str) -> list[str]:
    return [s.strip() for s in inp.split(",")] if inp else []


# NOTE: ListOf[T] still requires builtin str -> T conversion in pydantic.
_T = typing.TypeVar("_T")
SetOf = typing.Annotated[set[_T], pydantic.BeforeValidator(_to_list)]


class _BaseConfig(pydantic.BaseModel):
    class Config:
        alias_generator = str.upper

    @classmethod
    def from_env(cls) -> typing_extensions.Self:
        if cls is _BaseConfig:
            msg = f"{cls.__name__!r} is not instantiable."
            raise TypeError(msg)

        return cls(**os.environ)


class _BotConfig(_BaseConfig):
    DISCORD_TOKEN: typing.Final[str]
    DB_URI: typing.Final[str]
    DISCORD_IS_PROD: typing.Final[bool]
    SUPERUSER_IDS: typing.Final[SetOf[int]]


BOT_CONFIG: typing.Final[_BotConfig] = _BotConfig.from_env()

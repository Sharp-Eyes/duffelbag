"""Discord bot configuration from .env file."""

import os
import typing

import dotenv
import pydantic
import typing_extensions

__all__: typing.Sequence[str] = ("BOT_CONFIG",)

dotenv.load_dotenv()


class _BaseConfig(pydantic.BaseModel):
    class Config:
        alias_generator = str.upper

    @classmethod
    def from_env(cls) -> typing_extensions.Self:
        if cls is _BaseConfig:
            msg = f"{cls.__name__} is not instantiable."
            raise TypeError(msg)

        return cls(**os.environ)


class _BotConfig(_BaseConfig):
    DISCORD_TOKEN: typing.Final[str]
    DB_URI: typing.Final[str]


BOT_CONFIG: typing.Final[_BotConfig] = _BotConfig.from_env()

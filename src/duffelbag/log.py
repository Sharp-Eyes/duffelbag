"""Module containing logging config and customisation."""

import logging
import sys
import types
import typing
import warnings

import coloredlogs

__all__: typing.Sequence[str] = (
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "TRACE",
    "NOTSET",
    "get_logger",
    "initialise",
)

# Add new trace log level.
TRACE: typing.Final[int] = 5
logging.addLevelName(TRACE, "TRACE")


# Re-export existing log levels.
CRITICAL: typing.Final[int] = logging.CRITICAL
ERROR: typing.Final[int] = logging.ERROR
WARNING: typing.Final[int] = logging.WARNING
INFO: typing.Final[int] = logging.INFO
DEBUG: typing.Final[int] = logging.DEBUG
NOTSET: typing.Final[int] = logging.NOTSET


_SysExcInfoType = (
    tuple[type[BaseException], BaseException, types.TracebackType | None] | tuple[None, None, None]
)
_ExcInfoType = None | bool | _SysExcInfoType | BaseException


class DuffelbagLogger(logging.Logger):
    def trace(  # noqa: PLR0913
        self,
        msg: str,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: typing.Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'TRACE'.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.
        logger.trace("Houston, we have a %s", "tiny detail.", exc_info=1)
        """
        if self.isEnabledFor(TRACE):
            self._log(
                TRACE,
                msg,
                args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel,
                extra=extra,
            )


def initialise(level: int = TRACE) -> None:
    """Initialise logging for the Duffelbag bot."""
    logging.addLevelName(TRACE, "TRACE")
    logging.setLoggerClass(DuffelbagLogger)

    # HACK: Retroactively update logger class on any loggers that already exist.
    #       We only do this on actual logging.Loggers such that we don't
    #       accidentally break any existing loggers of a custom class.
    for logger in logging.root.manager.loggerDict.values():
        if type(logger) is logging.Logger:
            logger.__class__ = DuffelbagLogger

    logging.logThreads = False
    logging.logProcesses = False

    format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    root_logger = logging.getLogger()

    coloredlogs.DEFAULT_LEVEL_STYLES = {
        **coloredlogs.DEFAULT_LEVEL_STYLES,
        "trace": {"color": 246},
        "critical": {"background": "red"},
        "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
    }
    coloredlogs.DEFAULT_LOG_FORMAT = format_string

    warnings.simplefilter("always", DeprecationWarning)
    logging.captureWarnings(capture=True)

    coloredlogs.install(level=level, stream=sys.stdout)  # pyright: ignore[reportUnknownMemberType]

    root_logger.setLevel(level)
    get_logger("disnake").setLevel(WARNING)
    get_logger("websockets").setLevel(WARNING)
    get_logger("disnake.ext.plugins").setLevel(INFO)

    root_logger.log(TRACE, "Succesfully initialised loggers.")


# Re-export logging stuff.
def get_logger(name: str | None = None) -> DuffelbagLogger:
    """Alternative to logging.getLogger."""
    return typing.cast(DuffelbagLogger, logging.getLogger(name))

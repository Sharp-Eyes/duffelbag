"""Generic autocomplete implementations for discord."""

import typing

import rapidfuzz
import tanjun

AutocompleteValueT = typing.TypeVar("AutocompleteValueT", str, int, float)
RetT = typing.TypeVar("RetT")

ConverterSig = typing.Callable[
    typing.Concatenate[AutocompleteValueT, ...],
    RetT | typing.Coroutine[typing.Any, typing.Any, RetT],
]


class ChoicesProviderCallback(typing.Protocol[AutocompleteValueT]):
    def __call__(
        self,
        argument: str,
        /,
        *,
        min_results: int,
        max_results: int,
    ) -> typing.Mapping[str, AutocompleteValueT] | typing.Coroutine[typing.Any, typing.Any, typing.Mapping[str, AutocompleteValueT]]:
        ...


def find_best_choices(
    argument: str,
    /,
    *,
    objects: typing.Mapping[str, AutocompleteValueT],
    min_results: int,
    max_results: int,
    score_cutoff: float,
) -> typing.Mapping[str, AutocompleteValueT]:
    """Template function for autocompleters."""
    if not argument:
        # Truncate to first 25 options...
        return dict(
            pair
            for pair, _ in zip(objects.items(), range(25), strict=False)
        )

    matches = rapidfuzz.process.extract(
        argument,
        objects.keys(),
        processor=rapidfuzz.utils.default_process,
        limit=max_results,
    )

    options: typing.Mapping[str, AutocompleteValueT] = {}
    for i, (match, score, _) in enumerate(matches):
        # Only return results that match "well enough". If there aren't enough
        # results, return at least a given minimum.
        if i >= min_results and score < score_cutoff:
            break

        options[match] = objects[match]

    return options


def into_retry_converter(
    converter: ConverterSig[AutocompleteValueT, RetT | None],
    choices_provider: ChoicesProviderCallback,
) -> ConverterSig[AutocompleteValueT, RetT]:

    async def retry_converter(
        argument: AutocompleteValueT,
        *,
        ctx: tanjun.abc.SlashContext = tanjun.inject(type=tanjun.abc.SlashContext),
    ) -> RetT:
        # First try with actual input...
        result = await ctx.call_with_async_di(converter, argument)
        if result:
            return result

        # Retry with best match for input...
        choices = await ctx.call_with_async_di(
            choices_provider,
            argument,
            min_results=0,
            max_results=1,
        )
        if not choices:
            raise LookupError

        result = await ctx.call_with_async_di(converter, get_first_choice(choices))
        if result:
            return result

        raise LookupError

    return retry_converter


def into_autocompleter(
    option_provider: ChoicesProviderCallback[AutocompleteValueT],
) -> tanjun.abc.AutocompleteSig[AutocompleteValueT]:

    async def autocompleter(ctx: tanjun.abc.AutocompleteContext, argument: AutocompleteValueT, /) -> None:
        """Fuzzy-match over all arknights characters with at least one skill."""
        await ctx.set_choices(
            await ctx.call_with_async_di(
                option_provider,
                argument,
            ),
        )

    return autocompleter


def get_first_choice(choices: typing.Mapping[str, AutocompleteValueT]) -> AutocompleteValueT:
    return next(iter(choices.values()))


def get_command_option(option_name: str):
    def getter(ctx: tanjun.abc.AutocompleteContext = tanjun.inject(type=tanjun.abc.AutocompleteContext)):
        return ctx.options
"""Generic autocomplete implementations for discord."""

import typing

import rapidfuzz
import tanjun

OutT = typing.TypeVar("OutT", str, int, float)


class ChoicesProviderCallback(typing.Protocol):
    def __call__(
        self,
        argument: str,
        /,
        *,
        objects: typing.Mapping[str, OutT],
        min_results: int,
        max_results: int,
        score_cutoff: float,
    ) -> typing.Mapping[str, OutT]:
        ...


async def find_best_choices(
    argument: str,
    /,
    *,
    objects: typing.Mapping[str, OutT],
    min_results: int,
    max_results: int,
    score_cutoff: float,
) -> typing.Mapping[str, OutT]:
    """Template function for autocompleters."""
    if not argument:
        # Truncate to first 25 options...
        options: typing.Mapping[str, OutT] = dict(pair for pair, _ in zip(objects.items(), range(25), strict=False))

    else:
        matches = rapidfuzz.process.extract(
            argument,
            objects.keys(),
            processor=rapidfuzz.utils.default_process,
            limit=max_results,
        )

        options: typing.Mapping[str, OutT] = {}
        for i, (match, score, _) in enumerate(matches):
            # Only return results that match "well enough". If there aren't enough
            # results, return at least a given minimum.
            if i >= min_results and score < score_cutoff:
                break

            options[match] = objects[match]

    return options



RetT = typing.TypeVar("RetT")


async def retry_converter_factory(
    converter: typing.Callable[[str], RetT],
    option_provider: ChoicesProviderCallback,
):
    async def retry_converter(
        argument: str,
        *,
        ctx: tanjun.abc.SlashContext = tanjun.inject(type=tanjun.abc.SlashContext),
    ) -> RetT:
        # First try with actual input...
        result = await ctx.call_with_async_di(converter, argument)
        if result:
            return result

        options = await ctx.call_with_async_di(
            option_provider,
            argument,
            min_results=0,
            max_results=1,
        )
        if not options:
            raise LookupError

        best_match = next(iter(options.values()))
        return await ctx.call_with_async_di(converter, best_match)

    return retry_converter


async def autocompleter_factory(
    option_provider: ChoicesProviderCallback,
):
    async def autocompleter(ctx: tanjun.abc.AutocompleteContext, argument: str) -> None:
        """Fuzzy-match over all arknights characters with at least one skill."""
        await ctx.set_choices(
            await ctx.call_with_async_di(
                option_provider,
                argument,
            ),
        )

    return autocompleter

"""Foobar."""

import functools
import typing

import disnake
import rapidfuzz
from disnake.ext import commands, components, plugins

import database
from duffelbag import auth, user_data

plugin = plugins.Plugin()
manager = components.get_manager("duffelbag.user")


@plugin.slash_command(name="game-data")
async def game_data(_: disnake.CommandInteraction) -> None:
    """Commands to do with game-data."""


@game_data.sub_command(name="sync-characters")  # type: ignore
async def game_data_sync_characters(inter: disnake.CommandInteraction):
    await inter.response.defer(ephemeral=True)

    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )
    arknights_user = await auth.get_active_arknights_account(duffelbag_user)
    await user_data.store_characters(arknights_user)

    await inter.edit_original_message("Successfully synced your character data!")


@plugin.slash_command()
async def farm(_: disnake.CommandInteraction) -> None:
    """Set or view farming goals."""


@farm.sub_command_group(name="add-goal")  # pyright: ignore
async def farm_add_goal(_: disnake.CommandInteraction) -> None:
    """Set a new farming goal."""


@farm_add_goal.sub_command(name="skill")  # pyright: ignore
async def farm_add_goal_skill(
    inter: disnake.CommandInteraction,
    character_name: commands.String[
        str,
        1,
        32,
    ],  # W (1 char) ~ Skadi the Corrupting Heart (26 chars).
) -> None:
    """Add a skill mastery to your farming goals.

    Parameters
    ----------
    inter:
        The interaction from discord.
    character:
        The character for whom you wish to unlock masteries.

    """
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=inter.author.id,
        strict=True,
    )
    arknights_user = await auth.get_active_arknights_account(duffelbag_user)

    character = await user_data.get_character(character_name, arknights_user)

    initial = 0
    skill_localisations = await user_data.get_skill_localisations(character)
    skill_level = await user_data.get_skill_at_level(
        character,
        skill_id=skill_localisations[initial].skill_id,
        level=1,
    )

    wrapped = components.wrap_interaction(inter)
    await wrapped.response.send_message(
        embed=display_skill(character, skill_level, skill_localisations[initial]),
        components=SkillSelect.for_character(character, skill_localisations, initial=initial),
        ephemeral=True,
    )


THUMB_FMT = (
    "https://gamepress.gg/arknights/sites/arknights/files/game-images/skills/skill_icon_{}.png"
)


def display_skill(
    character: user_data.HybridCharacter,
    skill_level: user_data.HybridSkillLevel,
    skill_localisation: database.StaticSkillLocalisation,
) -> disnake.Embed:
    duration = "-" if skill_level.duration == -1 else skill_level.duration
    return disnake.Embed(
        title=f"**{character.name}**",
        description=(
            f"### Skill {skill_level.skill_num}\u2002•\u2002"
            f"{skill_localisation.name}\n\n"
            f"SP Cost: {skill_level.sp_cost}\u2002•\u2002"
            f"Initial SP: {skill_level.initial_sp}\u2002•\u2002"
            f"SP Charge Type: {skill_level.sp_type}\n"
            f"Skill Activation: {skill_level.skill_type}\u2002•\u2002"
            f"Duration: {duration}\n\n"
            f"{skill_localisation.description}"
        ),
    ).set_thumbnail(THUMB_FMT.format(skill_level.skill_id))


@manager.register
class SkillSelect(components.RichStringSelect):
    """Select menu that allows a user to select the skill they wish to farm for.

    An instance of this select is meant for one character.
    """

    max_values: int = 1

    character_id: str
    user_character_id: int

    @classmethod
    def for_character(
        cls,
        character: user_data.HybridCharacter,
        skills: typing.Sequence[database.StaticSkillLocalisation],
        *,
        initial: int = 0,
    ) -> "SkillSelect":
        options = [
            disnake.SelectOption(
                label=skill.name,
                value=skill.skill_id,
                default=(i == initial),
            )
            for i, skill in enumerate(skills)
        ]

        return cls(
            options=options,
            character_id=character.character_id,
            user_character_id=character.user_character_id,
        )

    async def callback(self, inter: components.MessageInteraction) -> None:
        ...


setup, teardown = plugin.create_extension_handlers()


async def character_autocomplete_template(
    _inter: disnake.CommandInteraction,
    input_: str,
    *,
    characters: dict[str, str],
    min_results: int,
    max_results: int,
    score_cutoff: float,
) -> dict[str, str]:
    """Template function for character autocompleters.

    Meant to be finalised using `functools.partial`, providing values for this
    function's keyword-arguments.
    """
    if not input_:
        # Truncate to first 25 options...
        return dict(pair for pair, _ in zip(characters.items(), range(25), strict=False))

    matches = rapidfuzz.process.extract(
        input_,
        characters.keys(),
        processor=rapidfuzz.utils.default_process,
        limit=max_results,
    )

    options: dict[str, str] = {}
    for i, (match, score, _) in enumerate(matches):
        # Only return results that match "well enough". If there aren't enough
        # results, return at least a given minimum.
        if i >= min_results and score < score_cutoff:
            break

        options[match] = characters[match]

    return options


@plugin.load_hook()
async def finalise_char_autocompleters() -> None:
    """Finalise the character autocomplete template with various settings for various commands."""
    characters = await database.StaticCharacter.objects()

    min_mastery_rarity = 4  # 3* ops and below cannot have masteries.
    mastery_autocomplete = functools.partial(
        character_autocomplete_template,
        characters={
            character.name: character.id
            for character in characters
            if character.rarity >= min_mastery_rarity
        },
        min_results=3,
        max_results=10,
        score_cutoff=80,
    )

    farm_add_goal_skill.autocomplete("character_name")(mastery_autocomplete)  # pyright: ignore

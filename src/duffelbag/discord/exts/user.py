"""Foobar."""

import functools
import typing

import hikari
import rapidfuzz
import ryoshu
import tanjun

import database
from duffelbag import auth, user_data

component = tanjun.Component(name="user")
manager = ryoshu.get_manager("duffelbag.user")


game_data_group = component.with_slash_command(tanjun.slash_command_group("game-data", "Do stuff with game data."))
farm_group = component.with_slash_command(tanjun.slash_command_group("farm", "Set or view farming goals."))
farm_add_goal_group = farm_group.make_sub_group("add-goal", "Set a new farming goal.")


@game_data_group.as_sub_command("sync-characters", "Sync your arknights characters.")
async def game_data_sync_characters(ctx: tanjun.abc.SlashContext) -> None:
    """Sync your arknights characters."""
    await ctx.defer(ephemeral=True)

    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
        strict=True,
    )
    arknights_user = await auth.get_active_arknights_account(duffelbag_user)
    await user_data.store_characters(arknights_user)

    await ctx.edit_last_response("Successfully synced your character data!")


@tanjun.with_str_slash_option(
    "character_name",
    "The character for whom you wish to farm a mastery.",
    min_length=1,  # W (1 char) ~ Skadi the Corrupting Heart (26 chars).
    max_length=32,
)
@farm_add_goal_group.as_sub_command("skill", "Add a skill mastery to your farming goals.")
async def farm_add_goal_skill(ctx: tanjun.abc.SlashContext, character_name: str) -> None:
    """Add a skill mastery to your farming goals.

    Parameters
    ----------
    ctx:
        The interaction from discord.
    character_name:
        The character for whom you wish to unlock masteries.

    """
    duffelbag_user = await auth.get_user_by_platform(
        platform=auth.Platform.DISCORD,
        platform_id=ctx.author.id,
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

    skill_select_menu = SkillSelect.for_character(character, skill_localisations, initial=initial)
    await ctx.create_initial_response(
        embed=display_skill(character, skill_level, skill_localisations[initial]),
        component=await ryoshu.into_action_row(skill_select_menu),
        ephemeral=True,
    )


THUMB_FMT = "https://gamepress.gg/arknights/sites/arknights/files/game-images/skills/skill_icon_{}.png"


def display_skill(
    character: user_data.HybridCharacter,
    skill_level: user_data.HybridSkillLevel,
    skill_localisation: database.StaticSkillLocalisation,
) -> hikari.Embed:
    """Display information about a skill in an embed."""
    duration = "-" if skill_level.duration == -1 else skill_level.duration
    return hikari.Embed(
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


@manager.register()
class SkillSelect(ryoshu.ManagedTextSelectMenu):
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
        """Make a SkillSelect for a given Arknights character."""
        options = [
            hikari.impl.SelectOptionBuilder(
                label=skill.name,
                value=skill.skill_id,
                is_default=(i == initial),
            )
            for i, skill in enumerate(skills)
        ]

        return cls(
            options=options,
            character_id=character.character_id,
            user_character_id=character.user_character_id,
        )

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:  # noqa: D102
        ...


async def character_autocomplete_template(  # noqa: PLR0913
    ctx: tanjun.abc.AutocompleteContext,
    input_: str,
    *,
    characters: dict[str, str],
    min_results: int,
    max_results: int,
    score_cutoff: float,
) -> None:
    """Template function for character autocompleters.

    Meant to be finalised using `functools.partial`, providing values for this
    function's keyword-arguments.
    """
    if not input_:
        # Truncate to first 25 options...
        options = dict(pair for pair, _ in zip(characters.items(), range(25), strict=False))

    else:
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

    await ctx.set_choices(options)


@component.with_client_callback(tanjun.ClientCallbackNames.STARTING)
async def finalise_char_autocompleters() -> None:
    """Finalise the character autocomplete template with various settings for various commands."""
    characters = await database.StaticCharacter.objects()

    # TODO: Maybe we can make this happen with DI somehow?
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

    farm_add_goal_skill.set_str_autocomplete("character_name", mastery_autocomplete)


loader = component.make_loader()

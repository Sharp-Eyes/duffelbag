"""Foobar."""

import decimal
import typing

import hikari
import ryoshu
import tanjun

import database
from duffelbag import auth, user_data
from duffelbag.discord import autocomplete

component = tanjun.Component(name="user")
manager = ryoshu.get_manager("duffelbag.user")


game_data_group = component.with_slash_command(tanjun.slash_command_group("game-data", "Do stuff with game data."))


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


async def _get_characters_with_skills() -> typing.Mapping[str, str]:
    joined = database.StaticCharacter.id.join_on(database.StaticCharacterSkill.character_id)
    characters = await (
        database.StaticCharacter.select(database.StaticCharacter.name, joined.character_id)
        .where(database.StaticCharacter.id == joined.character_id)
    )
    return {
        character["name"]: character["id.character_id"]
        for character in characters
    }


async def _into_character(argument: str) -> database.StaticCharacter | None:
    return await (
        database.StaticCharacter.objects()
        .where(database.StaticCharacter.id == argument)
        .first()
    )


async def _provide_skill_character_choices(
    argument: str,
    *,
    min_results: int = 3,
    max_results: int = 10,
    score_cutoff: float = 80.0,
    characters: typing.Mapping[str, str] = tanjun.cached_inject(_get_characters_with_skills),
) -> typing.Mapping[str, str]:
    return autocomplete.find_best_choices(
        argument,
        objects=characters,
        min_results=min_results,
        max_results=max_results,
        score_cutoff=score_cutoff,
    )


async def _into_skill(argument: str) -> database.StaticCharacterSkill:
    ...


async def _provide_skill_choices(
    argument: str,
    *,
    min_results: int = 3,
    max_results: int = 10,
    ctx: tanjun.abc.AutocompleteContext = tanjun.inject(type=tanjun.abc.AutocompleteContext),
) -> typing.Mapping[str, str]:
    character_id = ctx.options["character"].value
    assert isinstance(character_id, str)

    print(character_id)

    # Ensure we actually have a character...
    character_id = autocomplete.get_first_choice(
        await ctx.call_with_async_di(
            _provide_skill_character_choices,
            character_id,
            min_results=1,
            max_results=1,
        ),
    )

    joined = database.StaticSkillLocalisation.skill_id.join_on(database.StaticCharacterSkill.skill_id)
    skill_data = await (
        database.StaticSkillLocalisation.select(
            database.StaticSkillLocalisation.name,
            database.StaticSkillLocalisation.skill_id,
            joined.skill_num.as_alias("skill_num"),
        )
        .where(joined.character_id == character_id)
    )

    skill_choices = {skill["name"]: skill["skill_id"] for skill in skill_data}
    skill_choices |= {f"S{skill["skill_num"]}": skill["skill_id"] for skill in skill_data}

    return autocomplete.find_best_choices(
        argument,
        objects=skill_choices,
        min_results=3,
        max_results=10,
        score_cutoff=80,
    )


@tanjun.with_bool_slash_option(
    "hidden",
    "Whether you want other people to be able to see the result of this command.",
    default=True,
)
@tanjun.with_str_slash_option(
    "skill_level",
    "The level at which you want to check the skill.",
    default="MAX",
    key="skill_level_input",
)
@tanjun.with_str_slash_option(
    "skill",
    "The skill you want to check. If omitted, defaults to skill 1.",
    default="S1",
    autocomplete=autocomplete.into_autocompleter(_provide_skill_choices),
    key="skill_input",
)
@tanjun.with_str_slash_option(
    "character",
    "The character whose skills you want to check.",
    autocomplete=autocomplete.into_autocompleter(_provide_skill_character_choices),
    converters=autocomplete.into_retry_converter(_into_character, _provide_skill_character_choices),
    min_length=1,  # W (1 char) ~ Skadi the Corrupting Heart (26 chars).
    max_length=32,
)
@game_data_group.as_sub_command("skill", "Add a skill mastery to your farming goals.")
async def game_data_skill(
    ctx: tanjun.abc.SlashContext,
    character: database.StaticCharacter,
    skill_input: str,
    skill_level_input: str,
    *,
    hidden: bool = True,
) -> None:
    """Add a skill mastery to your farming goals.

    Parameters
    ----------
    ctx:
        The interaction from discord.
    character_id:
        The character for whom you wish to unlock masteries.
    hidden:
        Whether you want other people to be able to see the result of this command.

    """
    init_skill = 0
    init_level = 1

    skill_localisations = await user_data.get_skill_localisations(character)
    skill_localisation = skill_localisations[init_skill]
    skill_level = await user_data.get_skill_at_level(character, skill_id=skill_localisation.skill_id, level=init_level)
    skill_blackboards = await user_data.get_skill_level_blackboards(skill_level)

    skill_select_menu = SkillSelect.for_character(character, skill_localisations, initial=init_skill)
    level_select_menu = await SkillLevelSelect.for_skill_select(skill_select_menu, initial=init_level)

    await ctx.create_initial_response(
        embed=display_skill(
            character=character,
            skill_level=skill_level,
            skill_localisation=skill_localisation,
            blackboard=skill_blackboards,
        ),
        components=await ryoshu.into_action_rows([[skill_select_menu], [level_select_menu]]),
        ephemeral=hidden,
    )


THUMB_FMT = "https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets/refs/heads/cn/assets/torappu/dynamicassets/arts/skills/skill_icon_{skill_id}.png"
THUMB_FMT_SKCOM = "https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets/refs/heads/cn/assets/torappu/dynamicassets/arts/skills/skill_icon_{skill_id}/skill_icon_{skill_id}.png/skill_icon_{skill_id}.png"


def display_duration(duration: decimal.Decimal) -> str:
    """Turn a skill duration into a human-readable string."""
    return "\u221E" if duration == -1 else format(float(duration), "g")


SP_TYPE_DISPLAY_MAP = {
    "INCREASE_WHEN_ATTACK": "Offensive",
    "INCREASE_WHEN_TAKEN_DAMAGE": "Defensive",
    "INCREASE_WITH_TIME": "Auto",
    "ON_DEPLOYMENT": "Passive",
}

SKILL_TYPE_DISPLAY_MAP = {
    "AUTO": "Auto",
    "MANUAL": "Manual",
    "PASSIVE": "Passive",
}

DURATION_TYPE_DISPLAY_MAP = {
    "NONE": "Duration",
    "AMMO": "Ammo",
}

def display_skill(  # noqa: PLR0913
    *,
    character: str | database.StaticCharacter | user_data.HybridCharacter,
    skill_level: user_data.HybridSkillLevel,
    skill_level_diff: user_data.HybridSkillLevel | None = None,
    blackboard: typing.Sequence[database.StaticSkillBlackboard],
    blackboard_diff: typing.Sequence[database.StaticSkillBlackboard] | None = None,
    skill_localisation: database.StaticSkillLocalisation,
    sep: str = "\u2002\u2022\u2002",
    diff_sep: str = " \u2192 ",
) -> hikari.Embed:
    """Display information about a skill in an embed."""
    character_name = character if isinstance(character, str) else character.name

    if skill_level_diff is None:
        duration = display_duration(skill_level.duration)
        sp_cost = skill_level.sp_cost
        initial_sp = skill_level.initial_sp
        title_hint = user_data.display_skill_level(skill_level.level)
    else:
        duration = f"{display_duration(skill_level.duration)}{diff_sep}{display_duration(skill_level_diff.duration)}"
        sp_cost = f"{skill_level.sp_cost}{diff_sep}{skill_level_diff.sp_cost}"
        initial_sp = f"{skill_level.initial_sp}{diff_sep}{skill_level_diff.initial_sp}"
        title_hint = (
            f"Comparing {user_data.display_skill_level(skill_level.level)}{diff_sep}"
            f"{user_data.display_skill_level(skill_level_diff.level)}"
        )

    thumbnail_fmt = (THUMB_FMT_SKCOM if "skcom" in skill_level.skill_id else THUMB_FMT)
    thumbnail = thumbnail_fmt.format(skill_id=skill_level.skill_id)

    sp_type = SP_TYPE_DISPLAY_MAP[skill_level.sp_type]
    skill_type = SKILL_TYPE_DISPLAY_MAP[skill_level.skill_type]
    description = user_data.format_skill_description(
        skill_localisation,
        blackboard=blackboard,
        blackboard_diff=blackboard_diff,
        diff_sep=diff_sep,
    )

    return (
        hikari.Embed(
            title=f"**{character_name}**",
            description=(
                f"### {skill_localisation.name} (S{skill_level.skill_num}){sep}{title_hint}\n\n"
                f"SP Cost: **{sp_cost}**{sep}Initial SP: **{initial_sp}**{sep}Duration: **{duration}**\n"
                f"SP Recovery: **{sp_type}**{sep}Skill Activation: **{skill_type}**\n\n"
                f"{description}\n\n"
                f"-# Tip: select more than one level to compare stats!"
            ),
        )
        .set_thumbnail(thumbnail)
    )


@manager.register()
class SkillSelect(ryoshu.ManagedTextSelectMenu):
    """Select menu that allows a user to select a skill.

    An instance of this select is meant for one character.
    """

    max_values: int = 1

    character_name: str
    character_id: str

    @classmethod
    def for_character(
        cls,
        character: database.StaticCharacter,
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

        return cls(options=options, character_name=character.name, character_id=character.id)

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:  # noqa: D102
        assert isinstance(event.interaction, hikari.ComponentInteraction)
        selected_id = event.interaction.values[0]
        for option in self.options:
            option.set_is_default(option.value == selected_id)

        character = await (
            database.StaticCharacter.objects()
            .where(database.StaticCharacter.id == self.character_id)
            .first()
        )
        assert character

        skill_localisation = await user_data.get_skill_localisation(selected_id, character)
        skill_level = await user_data.get_skill_at_level(character, skill_id=selected_id, level=1)
        skill_blackboards = await user_data.get_skill_level_blackboards(skill_level)

        rows, _ = await manager.parse_message_components(event.interaction.message)
        await event.interaction.create_initial_response(
            response_type=hikari.ResponseType.MESSAGE_UPDATE,
            embed=display_skill(
                character=character,
                skill_level=skill_level,
                skill_localisation=skill_localisation,
                blackboard=skill_blackboards,
            ),
            components=await ryoshu.into_action_rows(rows),
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@manager.register()
class SkillLevelSelect(ryoshu.ManagedTextSelectMenu):
    """Select menu that allows a user to browse skill levels.

    Intended to be used in tandem with a SkillSelect.
    """

    max_values: int = 2

    @classmethod
    async def for_skill_select(cls, skill_select: SkillSelect, /, *, initial: int = 1) -> "SkillLevelSelect":
        """Make a skill level select menu for a corresponding skill select menu."""
        for option in skill_select.options:
            if option.is_default:
                skill_id = option.value
                break
        else:
            raise RuntimeError  # Unreachable

        skill_levels = await database.StaticSkillLevel.objects().where(database.StaticSkillLevel.skill_id == skill_id)
        options = [
            hikari.impl.SelectOptionBuilder(
                label=user_data.display_skill_level(skill_level),
                value=str(skill_level.level),
                is_default=(skill_level.level == initial),
            )
            for skill_level in skill_levels
        ]

        return cls(options=options)

    async def callback(self, event: hikari.InteractionCreateEvent) -> None:  # noqa: D102
        assert isinstance(event.interaction, hikari.ComponentInteraction)
        for option in self.options:
            option.set_is_default(option.value in event.interaction.values)

        rows, managed_components = await manager.parse_message_components(event.interaction.message)
        for component in managed_components:
            if isinstance(component, SkillSelect):
                break
        else:
            msg = "Could not find a SkillSelect."
            raise LookupError(msg)

        for option in component.options:
            if option.is_default:
                break
        else:
            raise RuntimeError  # Unreachable

        character_id = component.character_id
        character_name = component.character_name
        skill_id = option.value
        skill_localisation = await user_data.get_skill_localisation(skill_id, character_id)

        if len(event.interaction.values) == self.max_values:
            low, high = sorted(map(int, event.interaction.values))

            skill_level = await user_data.get_skill_at_level(character_id, skill_id, level=low)
            skill_level_diff = await user_data.get_skill_at_level(character_id, skill_id, level=high)
            skill_blackboards = await user_data.get_skill_level_blackboards(skill_level)
            skill_blackboards_diff = await user_data.get_skill_level_blackboards(skill_level_diff)

        else:
            level = int(event.interaction.values[0])

            skill_level = await user_data.get_skill_at_level(character_id, skill_id, level=level)
            skill_level_diff = None
            skill_blackboards = await user_data.get_skill_level_blackboards(skill_level)
            skill_blackboards_diff = None

        await event.interaction.create_initial_response(
            response_type=hikari.ResponseType.MESSAGE_UPDATE,
            embed=display_skill(
                character=character_name,
                skill_localisation=skill_localisation,
                skill_level=skill_level,
                skill_level_diff=skill_level_diff,
                blackboard=skill_blackboards,
                blackboard_diff=skill_blackboards_diff,
            ),
            components=await ryoshu.into_action_rows(rows),
            flags=hikari.MessageFlag.EPHEMERAL,
        )


loader = component.make_loader()

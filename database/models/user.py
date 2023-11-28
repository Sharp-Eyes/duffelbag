"""Database models storing user account character info.

Unlike the models in the `database.models.character` module, these modules
store the actual state of a character/their skills/their modules on a per-user
basis.
"""

from piccolo import columns, table

from database.models import auth, static


class UserCharacter(table.Table):
    """The database representation of a character on the Arknights API."""

    id: columns.Serial
    character_id = columns.ForeignKey(references=static.StaticCharacter)
    user_id = columns.ForeignKey(references=auth.ArknightsUser)
    main_skill_lvl = columns.SmallInt()
    level = columns.SmallInt()
    exp = columns.SmallInt()  # Max EXP is 31143, max SmallInt is 32767.
    evolve_phase = columns.SmallInt()

    # NOTE: As of migration 2023-11-22T00:33:34:498866, there is a composite
    #       unique constraint on (character_id, user_id) with name
    #       "user_character_character_id_user_id_key".


class UserCharacterSkill(table.Table):
    """The database representation of a character's skill on the Arknights API."""

    id: columns.Serial
    skill_id = columns.ForeignKey(references=static.StaticSkill)
    user_character_id = columns.ForeignKey(references=UserCharacter)
    specialize_level = columns.SmallInt()

    # NOTE: As of migration 2023-11-22T00:33:34:498866, there is a composite
    #       unique constraint on (skill_id, user_character_id) with name
    #       "user_character_skill_skill_id_character_id_key".


class UserCharacterModule(table.Table):
    """The database representation of a character's module on the Arknights API."""

    id: columns.Serial
    module_id = columns.Varchar(20)
    user_character_id = columns.ForeignKey(references=UserCharacter)
    level = columns.SmallInt()

    # NOTE: As of migration 2023-11-22T00:33:34:498866, there is a composite
    #       unique constraint on (module_id, user_character_id) with name
    #       "user_character_module_module_id_character_id_key".

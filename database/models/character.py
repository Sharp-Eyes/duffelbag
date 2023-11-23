"""Database models storing static character info."""

from piccolo import columns, table


class Character(table.Table):
    """The database representation of static information on an Arknights character."""

    id = columns.Varchar(20, primary_key=True)
    name = columns.Varchar(50)
    rarity = columns.SmallInt()
    profession = columns.Varchar(length=16)
    sub_profession = columns.Varchar(length=16)
    is_alter = columns.Boolean()


class Tag(table.Table):
    """The database representation of a recruitment tag of an Arknights character."""

    name = columns.Varchar(16, primary_key=True)


class Skill(table.Table):
    """The database representation of character-specific information on a skill.

    This is a one (Character) to many (Skill) relationship.
    """

    id: columns.Serial
    character_id = columns.ForeignKey(references=Character)
    skill_id = columns.Varchar(20)
    display_id = columns.Varchar(20, null=True)


class Item(table.Table):
    """The database representation of static information on an item."""

    id = columns.Varchar(20, primary_key=True)
    icon_id = columns.Varchar(20)
    name = columns.Varchar(50)
    description = columns.Varchar(500)
    rarity = columns.SmallInt()


class CharacterTag(table.Table):
    """A database meta-table linking a Character to a Tag.

    This is a one (Character) to many (Tag) relationship.
    """

    id: columns.Serial
    character = columns.ForeignKey(Character)
    tag = columns.ForeignKey(Tag)


class CharacterElitePhase(table.Table):
    """The database representation of static information on an elite phase (e.g. Elite 1).

    This is a one (Character) to many (CharacterElitePhase) relationship.
    """

    id: columns.Serial
    character = columns.ForeignKey(Character)
    level = columns.SmallInt()

    # TODO: Elite phase stat blocks


class CharacterElitePhaseItem(table.Table):
    """A database meta-table linking an Item to a CharacterElitePhase.

    This is a one (CharacterElitePhase) to many (Item) relationship.

    Additionally contains the required quantity of the designated Item.
    """

    id: columns.Serial
    elite_phase = columns.ForeignKey(CharacterElitePhase)
    item = columns.ForeignKey(Item)
    quantity = columns.SmallInt()


class SkillSharedUpgrade(table.Table):
    """The database representation of static information on global skill level upgrades.

    This accounts for the first seven levels of skill upgrades, where a single
    upgrade affects all skills.

    This is a one (Character) to many (SkillSharedUpgrade) relationship.
    """

    id: columns.Serial
    character = columns.ForeignKey(Character)
    level = columns.SmallInt()


class SkillSharedUpgradeItem(table.Table):
    """A database meta-table linking an Item to a SkillSharedUpgrade.

    This is a one (SkillSharedUpgrade) to many (Item) relationship.

    Additionally contains the required quantity of the designated Item.
    """

    id: columns.Serial
    upgrade = columns.ForeignKey(SkillSharedUpgrade)
    item = columns.ForeignKey(Item)
    quantity = columns.SmallInt()


class SkillMastery(table.Table):
    """The database representation of static information on a skill's mastery levels.

    This is a one (Skill) to many (SkillMastery) relation.
    """

    id: columns.Serial
    skill = columns.ForeignKey(Skill)
    level = columns.SmallInt()


class SkillMasteryItem(table.Table):
    """A database meta-table linking an Item to a SkillMastery.

    This is a one (SkillMastery) to many (Item) relationship.

    Additionally contains the required quantity of the designated Item.
    """

    id: columns.Serial
    mastery = columns.ForeignKey(SkillMastery)
    item = columns.ForeignKey(Item)
    quantity = columns.SmallInt()


# TODO: add modules

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Boolean
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import SmallInt
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class Character(Table, tablename="character", schema=None):
    id = Varchar(
        length=20,
        default="",
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class CharacterElitePhase(Table, tablename="character_elite_phase", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class Item(Table, tablename="item", schema=None):
    id = Varchar(
        length=20,
        default="",
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class Skill(Table, tablename="skill", schema=None):
    id = Varchar(
        length=20,
        default="",
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class SkillMastery(Table, tablename="skill_mastery", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class SkillSharedUpgrade(Table, tablename="skill_shared_upgrade", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


class Tag(Table, tablename="tag", schema=None):
    name = Varchar(
        length=16,
        default="",
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


ID = "2023-05-30T11:45:24:800756"
VERSION = "0.112.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="Item", tablename="item", schema=None, columns=None
    )

    manager.add_table(
        class_name="Character", tablename="character", schema=None, columns=None
    )

    manager.add_table(
        class_name="Skill", tablename="skill", schema=None, columns=None
    )

    manager.add_table(
        class_name="SkillSharedUpgradeItem",
        tablename="skill_shared_upgrade_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="CharacterElitePhaseItem",
        tablename="character_elite_phase_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="SkillSharedUpgrade",
        tablename="skill_shared_upgrade",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="CharacterTag",
        tablename="character_tag",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="SkillMastery",
        tablename="skill_mastery",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Tag", tablename="tag", schema=None, columns=None
    )

    manager.add_table(
        class_name="SkillMasteryItem",
        tablename="skill_mastery_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="CharacterElitePhase",
        tablename="character_elite_phase",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="Item",
        tablename="item",
        column_name="id",
        db_column_name="id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 20,
            "default": "",
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Item",
        tablename="item",
        column_name="icon_id",
        db_column_name="icon_id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 20,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Item",
        tablename="item",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 50,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Item",
        tablename="item",
        column_name="description",
        db_column_name="description",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 500,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Item",
        tablename="item",
        column_name="rarity",
        db_column_name="rarity",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="id",
        db_column_name="id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 20,
            "default": "",
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 50,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="rarity",
        db_column_name="rarity",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="profession",
        db_column_name="profession",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 16,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="sub_profession",
        db_column_name="sub_profession",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 16,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Character",
        tablename="character",
        column_name="is_alter",
        db_column_name="is_alter",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Skill",
        tablename="skill",
        column_name="id",
        db_column_name="id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 20,
            "default": "",
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Skill",
        tablename="skill",
        column_name="display_id",
        db_column_name="display_id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 20,
            "default": "",
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillSharedUpgradeItem",
        tablename="skill_shared_upgrade_item",
        column_name="upgrade",
        db_column_name="upgrade",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": SkillSharedUpgrade,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillSharedUpgradeItem",
        tablename="skill_shared_upgrade_item",
        column_name="item",
        db_column_name="item",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Item,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillSharedUpgradeItem",
        tablename="skill_shared_upgrade_item",
        column_name="quantity",
        db_column_name="quantity",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterElitePhaseItem",
        tablename="character_elite_phase_item",
        column_name="elite_phase",
        db_column_name="elite_phase",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": CharacterElitePhase,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterElitePhaseItem",
        tablename="character_elite_phase_item",
        column_name="item",
        db_column_name="item",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Item,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterElitePhaseItem",
        tablename="character_elite_phase_item",
        column_name="quantity",
        db_column_name="quantity",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillSharedUpgrade",
        tablename="skill_shared_upgrade",
        column_name="character",
        db_column_name="character",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Character,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillSharedUpgrade",
        tablename="skill_shared_upgrade",
        column_name="level",
        db_column_name="level",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterTag",
        tablename="character_tag",
        column_name="character",
        db_column_name="character",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Character,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterTag",
        tablename="character_tag",
        column_name="tag",
        db_column_name="tag",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Tag,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMastery",
        tablename="skill_mastery",
        column_name="character",
        db_column_name="character",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Character,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMastery",
        tablename="skill_mastery",
        column_name="skill",
        db_column_name="skill",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Skill,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMastery",
        tablename="skill_mastery",
        column_name="level",
        db_column_name="level",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="Tag",
        tablename="tag",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 16,
            "default": "",
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMasteryItem",
        tablename="skill_mastery_item",
        column_name="mastery",
        db_column_name="mastery",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": SkillMastery,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMasteryItem",
        tablename="skill_mastery_item",
        column_name="item",
        db_column_name="item",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Item,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="SkillMasteryItem",
        tablename="skill_mastery_item",
        column_name="quantity",
        db_column_name="quantity",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterElitePhase",
        tablename="character_elite_phase",
        column_name="character",
        db_column_name="character",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Character,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    manager.add_column(
        table_class_name="CharacterElitePhase",
        tablename="character_elite_phase",
        column_name="level",
        db_column_name="level",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
    )

    return manager

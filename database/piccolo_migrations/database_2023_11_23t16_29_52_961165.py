from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
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


ID = "2023-11-23T16:29:52:961165"
VERSION = "1.1.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="SkillMastery",
        tablename="skill_mastery",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="SkillMasteryItem",
        tablename="skill_mastery_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="Skill", tablename="skill", schema=None, columns=None
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
        schema=None,
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
        schema=None,
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
        schema=None,
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
        schema=None,
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
        schema=None,
    )

    manager.add_column(
        table_class_name="Skill",
        tablename="skill",
        column_name="character_id",
        db_column_name="character_id",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="Skill",
        tablename="skill",
        column_name="skill_id",
        db_column_name="skill_id",
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
        schema=None,
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
        schema=None,
    )

    return manager

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Decimal
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import SmallInt
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table
import decimal


class StaticSkill(Table, tablename="static_skill", schema=None):
    id = Varchar(
        length=64,
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


class StaticSkillLevel(Table, tablename="static_skill_level", schema=None):
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


ID = "2023-11-28T17:00:29:354896"
VERSION = "1.1.1"
DESCRIPTION = "add static skill models"


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="StaticSkillLocalisation",
        tablename="static_skill_localisation",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkill",
        tablename="static_skill",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillBlackboard",
        tablename="static_skill_blackboard",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillLevel",
        tablename="static_skill_level",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="StaticSkillLocalisation",
        tablename="static_skill_localisation",
        column_name="skill_id",
        db_column_name="skill_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticSkill,
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
        table_class_name="StaticSkillLocalisation",
        tablename="static_skill_localisation",
        column_name="locale",
        db_column_name="locale",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 8,
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
        table_class_name="StaticSkillLocalisation",
        tablename="static_skill_localisation",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 64,
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
        table_class_name="StaticSkillLocalisation",
        tablename="static_skill_localisation",
        column_name="description",
        db_column_name="description",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1024,
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
        table_class_name="StaticSkill",
        tablename="static_skill",
        column_name="id",
        db_column_name="id",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 64,
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticSkill",
        tablename="static_skill",
        column_name="skill_type",
        db_column_name="skill_type",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
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
        table_class_name="StaticSkill",
        tablename="static_skill",
        column_name="sp_type",
        db_column_name="sp_type",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
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
        table_class_name="StaticSkill",
        tablename="static_skill",
        column_name="duration_type",
        db_column_name="duration_type",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
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
        table_class_name="StaticSkillBlackboard",
        tablename="static_skill_blackboard",
        column_name="skill_level_id",
        db_column_name="skill_level_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticSkillLevel,
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
        table_class_name="StaticSkillBlackboard",
        tablename="static_skill_blackboard",
        column_name="key",
        db_column_name="key",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 64,
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
        table_class_name="StaticSkillBlackboard",
        tablename="static_skill_blackboard",
        column_name="value",
        db_column_name="value",
        column_class_name="Decimal",
        column_class=Decimal,
        params={
            "default": decimal.Decimal("0"),
            "digits": (8, 4),
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
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="skill_id",
        db_column_name="skill_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticSkill,
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
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="sp_cost",
        db_column_name="sp_cost",
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
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="initial_sp",
        db_column_name="initial_sp",
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
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="charges",
        db_column_name="charges",
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
        table_class_name="StaticSkillLevel",
        tablename="static_skill_level",
        column_name="duration",
        db_column_name="duration",
        column_class_name="Decimal",
        column_class=Decimal,
        params={
            "default": decimal.Decimal("0"),
            "digits": (8, 4),
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

    manager.alter_column(
        table_class_name="StaticCharacterSkill",
        tablename="static_character_skill",
        column_name="skill_id",
        db_column_name="skill_id",
        params={
            "references": StaticSkill,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
        },
        old_params={
            "references": None,
            "on_delete": None,
            "on_update": None,
            "target_column": None,
            "null": False,
        },
        column_class=ForeignKey,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="UserCharacterSkill",
        tablename="user_character_skill",
        column_name="skill_id",
        db_column_name="skill_id",
        params={
            "references": StaticSkill,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
        },
        old_params={
            "references": None,
            "on_delete": None,
            "on_update": None,
            "target_column": None,
            "null": False,
        },
        column_class=ForeignKey,
        old_column_class=Varchar,
        schema=None,
    )

    return manager

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import BigInt
from piccolo.columns.column_types import Boolean
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import SmallInt
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class ArknightsUser(Table, tablename="arknights_user", schema=None):
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


class DuffelbagUser(Table, tablename="duffelbag_user", schema=None):
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


class StaticCharacter(Table, tablename="static_character", schema=None):
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


class StaticCharacterElitePhase(
    Table, tablename="static_character_elite_phase", schema=None
):
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


class StaticItem(Table, tablename="static_item", schema=None):
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


class StaticSkill(Table, tablename="static_skill", schema=None):
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


class StaticSkillMastery(Table, tablename="static_skill_mastery", schema=None):
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


class StaticSkillSharedUpgrade(
    Table, tablename="static_skill_shared_upgrade", schema=None
):
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


class StaticTag(Table, tablename="static_tag", schema=None):
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


class UserCharacter(Table, tablename="user_character", schema=None):
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


ID = "2023-11-23T20:25:10:694640"
VERSION = "1.1.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="database", description=DESCRIPTION
    )

    manager.add_table(
        class_name="StaticCharacter",
        tablename="static_character",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="UserCharacterModule",
        tablename="user_character_module",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticItem",
        tablename="static_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticTag", tablename="static_tag", schema=None, columns=None
    )

    manager.add_table(
        class_name="StaticCharacterElitePhaseItem",
        tablename="static_character_elite_phase_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="ArknightsUser",
        tablename="arknights_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillSharedUpgrade",
        tablename="static_skill_shared_upgrade",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="UserCharacter",
        tablename="user_character",
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
        class_name="PlatformUser",
        tablename="platform_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="UserCharacterSkill",
        tablename="user_character_skill",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticCharacterElitePhase",
        tablename="static_character_elite_phase",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillMastery",
        tablename="static_skill_mastery",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="DuffelbagUser",
        tablename="duffelbag_user",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticCharacterTag",
        tablename="static_character_tag",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillSharedUpgradeItem",
        tablename="static_skill_shared_upgrade_item",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="StaticSkillMasteryItem",
        tablename="static_skill_mastery_item",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacter",
        tablename="static_character",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="UserCharacterModule",
        tablename="user_character_module",
        column_name="module_id",
        db_column_name="module_id",
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
        table_class_name="UserCharacterModule",
        tablename="user_character_module",
        column_name="user_character_id",
        db_column_name="user_character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": UserCharacter,
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
        table_class_name="UserCharacterModule",
        tablename="user_character_module",
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
        table_class_name="StaticItem",
        tablename="static_item",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticItem",
        tablename="static_item",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticItem",
        tablename="static_item",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticItem",
        tablename="static_item",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticItem",
        tablename="static_item",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticTag",
        tablename="static_tag",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="StaticCharacterElitePhaseItem",
        tablename="static_character_elite_phase_item",
        column_name="elite_phase_id",
        db_column_name="elite_phase_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticCharacterElitePhase,
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
        table_class_name="StaticCharacterElitePhaseItem",
        tablename="static_character_elite_phase_item",
        column_name="item_id",
        db_column_name="item_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticItem,
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
        table_class_name="StaticCharacterElitePhaseItem",
        tablename="static_character_elite_phase_item",
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
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
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
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="channel_uid",
        db_column_name="channel_uid",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="yostar_token",
        db_column_name="yostar_token",
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
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="server",
        db_column_name="server",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 4,
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
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="active",
        db_column_name="active",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="ArknightsUser",
        tablename="arknights_user",
        column_name="game_uid",
        db_column_name="game_uid",
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
        table_class_name="StaticSkillSharedUpgrade",
        tablename="static_skill_shared_upgrade",
        column_name="character_id",
        db_column_name="character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticCharacter,
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
        table_class_name="StaticSkillSharedUpgrade",
        tablename="static_skill_shared_upgrade",
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
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
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
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="arknights_id",
        db_column_name="arknights_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": ArknightsUser,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="ScheduledArknightsUserDeletion",
        tablename="scheduled_arknights_user_deletion",
        column_name="deletion_ts",
        db_column_name="deletion_ts",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
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
        table_class_name="UserCharacter",
        tablename="user_character",
        column_name="character_id",
        db_column_name="character_id",
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
        table_class_name="UserCharacter",
        tablename="user_character",
        column_name="user_id",
        db_column_name="user_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": ArknightsUser,
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
        table_class_name="UserCharacter",
        tablename="user_character",
        column_name="main_skill_lvl",
        db_column_name="main_skill_lvl",
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
        table_class_name="UserCharacter",
        tablename="user_character",
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
        table_class_name="UserCharacter",
        tablename="user_character",
        column_name="exp",
        db_column_name="exp",
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
        table_class_name="UserCharacter",
        tablename="user_character",
        column_name="evolve_phase",
        db_column_name="evolve_phase",
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
        table_class_name="StaticSkill",
        tablename="static_skill",
        column_name="character_id",
        db_column_name="character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticCharacter,
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
        table_class_name="StaticSkill",
        tablename="static_skill",
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
        table_class_name="StaticSkill",
        tablename="static_skill",
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

    manager.add_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
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
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="platform_id",
        db_column_name="platform_id",
        column_class_name="BigInt",
        column_class=BigInt,
        params={
            "default": 0,
            "null": True,
            "primary_key": False,
            "unique": True,
            "index": True,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="PlatformUser",
        tablename="platform_user",
        column_name="platform_name",
        db_column_name="platform_name",
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
        schema=None,
    )

    manager.add_column(
        table_class_name="UserCharacterSkill",
        tablename="user_character_skill",
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
        table_class_name="UserCharacterSkill",
        tablename="user_character_skill",
        column_name="user_character_id",
        db_column_name="user_character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": UserCharacter,
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
        table_class_name="UserCharacterSkill",
        tablename="user_character_skill",
        column_name="specialize_level",
        db_column_name="specialize_level",
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
        table_class_name="StaticCharacterElitePhase",
        tablename="static_character_elite_phase",
        column_name="character_id",
        db_column_name="character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticCharacter,
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
        table_class_name="StaticCharacterElitePhase",
        tablename="static_character_elite_phase",
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
        table_class_name="StaticSkillMastery",
        tablename="static_skill_mastery",
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
        table_class_name="StaticSkillMastery",
        tablename="static_skill_mastery",
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
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="username",
        db_column_name="username",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 32,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="DuffelbagUser",
        tablename="duffelbag_user",
        column_name="password",
        db_column_name="password",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 97,
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
        table_class_name="StaticCharacterTag",
        tablename="static_character_tag",
        column_name="character_id",
        db_column_name="character_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticCharacter,
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
        table_class_name="StaticCharacterTag",
        tablename="static_character_tag",
        column_name="tag_id",
        db_column_name="tag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticTag,
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
        table_class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
        column_name="duffelbag_id",
        db_column_name="duffelbag_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": DuffelbagUser,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="ScheduledUserDeletion",
        tablename="scheduled_user_deletion",
        column_name="deletion_ts",
        db_column_name="deletion_ts",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
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
        table_class_name="StaticSkillSharedUpgradeItem",
        tablename="static_skill_shared_upgrade_item",
        column_name="skill_upgrade_id",
        db_column_name="skill_upgrade_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticSkillSharedUpgrade,
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
        table_class_name="StaticSkillSharedUpgradeItem",
        tablename="static_skill_shared_upgrade_item",
        column_name="item_id",
        db_column_name="item_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticItem,
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
        table_class_name="StaticSkillSharedUpgradeItem",
        tablename="static_skill_shared_upgrade_item",
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
        table_class_name="StaticSkillMasteryItem",
        tablename="static_skill_mastery_item",
        column_name="mastery_id",
        db_column_name="mastery_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticSkillMastery,
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
        table_class_name="StaticSkillMasteryItem",
        tablename="static_skill_mastery_item",
        column_name="item_id",
        db_column_name="item_id",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": StaticItem,
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
        table_class_name="StaticSkillMasteryItem",
        tablename="static_skill_mastery_item",
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

    return manager

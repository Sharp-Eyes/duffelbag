"""Database models storing bot user authentication info."""

from piccolo import columns, table


class DuffelbagUser(table.Table):
    """The database representation of a user of Duffelbag.

    The auto-incrementing id is used internally to link accounts between
    different platforms and alts on the same platform. Currently planning to
    support Discord and Eludris.
    """

    id: columns.Serial
    username = columns.Varchar(32, unique=True)

    # This is the length of an argon2-encoded string with hash length 32.
    password = columns.Varchar(97)


class PlatformUser(table.Table):
    """A database meta-table linking a Duffelbag user to a user of an external platform.

    This is a one (DuffelbagUser) to many (PlatformUser) relationship.
    """

    id: columns.Serial
    user = columns.ForeignKey(DuffelbagUser)
    platform_id = columns.BigInt(null=True, unique=True, index=True)
    platform_name = columns.Varchar(16)

    # NOTE: As of migration 2023-05-31T10:47:00:954167, there is a composite
    #       unique constraint on (platform_id, platform_name) with name
    #       "platform_user_platform_id_platform_name_key".


class ArknightsUser(table.Table):
    """The database representation of a user's Arknights authentication data."""

    id: columns.Serial
    user = columns.ForeignKey(DuffelbagUser)
    channel_uid = columns.Varchar(16)
    yostar_token = columns.Varchar(32)
    server = columns.Varchar(4)
    active = columns.Boolean()
    game_uid = columns.Varchar(8)  # TODO: Validate whether 8 is enough

    # NOTE: As of migration 2023-05-31T10:47:00:954167, there is a composite
    #       unique constraint on (channel_uid, yostar_token) with name
    #       "arknights_user_channel_uid_yostar_token_key".


class ScheduledUserDeletion(table.Table):
    """The database representation of a scheduled user deletion.

    If a user no longer shares any guilds with the bot or requests that their
    account be deleted, deletion will be scheduled in the near future.

    This is a one (DuffelbagUser) to one (ScheduledUserDeletion) relation.
    """

    id: columns.Serial
    user = columns.ForeignKey(DuffelbagUser, unique=True)
    deletion_ts = columns.Timestamptz()

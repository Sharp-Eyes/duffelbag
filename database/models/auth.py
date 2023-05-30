"""Database models storing bot user authentication info."""

from piccolo import columns, table


class UserIdentity(table.Table):
    """The database representation of a user of Duffelbag.

    The auto-incrementing id is used internally to link accounts between
    different platforms. Currently planning to support Discord and Eludris.
    """

    id: columns.Serial
    discord_id = columns.BigInt(null=True, unique=True, index=True)
    eludris_id = columns.BigInt(null=True, unique=True, index=True)


class Auth(table.Table):
    """The database representation of a user's Arknights authentication data."""

    user = columns.ForeignKey(references=UserIdentity)
    channel_uid = columns.Varchar(16)
    yostar_token = columns.Varchar(32)

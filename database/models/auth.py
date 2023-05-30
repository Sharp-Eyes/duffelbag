"""Database models storing bot user authentication info."""

from piccolo import columns, table


class DuffelbagUser(table.Table):
    """The database representation of a user of Duffelbag.

    The auto-incrementing id is used internally to link accounts between
    different platforms and alts on the same platform. Currently planning to
    support Discord and Eludris.
    """

    id: columns.Serial

    # TODO: User settings.


class PlatformUser(table.Table):
    """A database meta-table linking a Duffelbag user to a user of an external platform.

    This is a one (DuffelbagUser) to many (PlatformUser) relationship.
    """

    id: columns.Serial
    user = columns.ForeignKey(DuffelbagUser)
    platform_id = columns.BigInt(null=True, unique=True, index=True)
    platform_name = columns.Varchar(16)

    # TODO: Perhaps a composite unique constraint on (platform_id, platform_name)


class Auth(table.Table):
    """The database representation of a user's Arknights authentication data."""

    id: columns.Serial
    user = columns.ForeignKey(references=DuffelbagUser)
    channel_uid = columns.Varchar(16)
    yostar_token = columns.Varchar(32)

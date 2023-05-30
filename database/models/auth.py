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
    password = columns.Varchar(32)


class PlatformUser(table.Table):
    """A database meta-table linking a Duffelbag user to a user of an external platform.

    This is a one (DuffelbagUser) to many (PlatformUser) relationship.
    """

    id: columns.Serial
    user = columns.ForeignKey(DuffelbagUser)
    platform_id = columns.BigInt(null=True, unique=True, index=True)
    platform_name = columns.Varchar(16)

    # TODO: Perhaps a composite unique constraint on (platform_id, platform_name)


class ArknightsUser(table.Table):
    """The database representation of a user's Arknights authentication data."""

    id: columns.Serial
    user = columns.ForeignKey(references=DuffelbagUser)
    channel_uid = columns.Varchar(16)
    yostar_token = columns.Varchar(32)

    # NOTE: Email only serves to pre-warn when a user tries to register with an
    #       account that is already registered. Since it's privacy-sensitive
    #       information, we'll keep it nullable and opt-in.
    email = columns.Email(null=True)

    # TODO: Perhaps a composite unique constraint on (user, channel_uid, yostar_token)

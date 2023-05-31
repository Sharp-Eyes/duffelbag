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

    # NOTE: As of migration 2023-05-31T10:47:00:954167, there is a composite
    #       unique constraint on (platform_id, platform_name) with name
    #       "platform_user_platform_id_platform_name_key".


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

    # NOTE: As of migration 2023-05-31T10:47:00:954167, there is a composite
    #       unique constraint on (channel_uid, yostar_token) with name
    #       "arknights_user_channel_uid_yostar_token_key".

"""Module containing exceptions raised by the Duffelbag bot."""

import datetime
import typing

import attrs


@attrs.define(auto_exc=True, slots=False, init=False)
class DuffelbagError(Exception):
    """Base exception class for exceptions raised by Duffelbag."""

    message: str
    """Error message for internal use."""

    def to_dict(self) -> dict[str, object]:
        """Return a dict mapping field name to value for localisation string formatting."""
        return attrs.asdict(self)


@attrs.define(auto_exc=True, slots=False, init=False)
class AuthError(DuffelbagError):
    """Base exception class for exceptions raised as part of authentication."""


@attrs.define(auto_exc=True, slots=False, init=True)
class CredentialSizeViolationError(DuffelbagError):
    """Login credentials were too short or too long."""

    credential: str
    min_size: int
    max_size: int


@attrs.define(auto_exc=True, slots=False, init=True)
class CredentialCharacterViolationError(DuffelbagError):
    """Login credentials used invalid characters."""

    credential: str
    allowed_chars: str


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagUserExistsError(AuthError):
    """A new user could not be created because it conflicts with an existing one."""

    username: str
    """The username of the Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class LoginError(AuthError):
    """Invalid credentials for an account were provided."""

    account_type: typing.Literal["Duffelbag", "Platform", "Arknights"]
    """The type of account. Can be 'Duffelbag', 'Platform' or 'Arknights'."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagDeletionAlreadyQueuedError(AuthError):
    """A user tried to delete a Duffelbag account that is already scheduled for deletion."""

    username: str
    """The username of the Duffelbag account."""
    deletion_ts: datetime.datetime
    """The timestamp at which the Duffelbag account is to be deleted."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagDeletionNotQueuedError(AuthError):
    """Tried to get a Duffelbag account that is not scheduled for deletion."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagConnectionNotFoundError(AuthError):
    """Could not find a duffelbag account for a given platform account."""

    platform_id: int
    """The user id of the platform account."""
    platform: str
    """The name of the target platform."""


@attrs.define(auto_exc=True, slots=False, init=True)
class PlatformConnectionExistsError(AuthError):
    """Attempted to connect the same external account to two different Duffelbag accounts."""

    username: str
    """The username of the Duffelbag account."""
    existing_username: str
    """The username of the existing Duffelbag account."""
    is_own: bool
    """Whether the platform account is registered to the same Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class PlatformConnectionNotFoundError(AuthError):
    """Could not find a connected account for a given Duffelbag account."""

    username: str
    """The username of the Duffelbag account."""
    platform: str
    """The name of the target platform."""


@attrs.define(auto_exc=True, slots=False, init=True)
class ArknightsConnectionExistsError(AuthError):
    """Attempted to connect the same Arknights account to two different Duffelbag accounts."""

    username: str
    """The username of the Duffelbag account that made the request."""
    existing_username: str
    """The username of the existing Duffelbag account."""
    is_own: bool
    """Whether the Arknights account is registered to the same Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class NoActiveAccountError(AuthError):
    """No Arknights account was designated as the active account for the given Duffelbag account."""

    username: str
    """The username of the Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class InvalidEmailError(AuthError):
    """Attempted to bind an Arknights account with an invalid email address."""

    email: str
    """The invalid email address."""

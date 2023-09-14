"""Module containing exceptions raised by the Duffelbag bot."""

import datetime

import attrs


@attrs.define(auto_exc=True, slots=False, init=False)
class DuffelbagException(Exception):
    """Base exception class for exceptions raised by Duffelbag."""

    message: str
    """Error message for internal use."""

    def to_dict(self) -> dict[str, object]:
        """Return a dict mapping field name to value for localisation string formatting."""
        return attrs.asdict(self)


@attrs.define(auto_exc=True, slots=False, init=False)
class AuthException(DuffelbagException):
    """Base exception class for exceptions raised as part of authentication."""


@attrs.define(auto_exc=True, slots=False, init=True)
class CredentialSizeViolation(DuffelbagException):
    """Login credentials were too short or too long."""

    credential: str
    min: int
    max: int


@attrs.define(auto_exc=True, slots=False, init=True)
class CredentialCharacterViolation(DuffelbagException):
    """Login credentials used invalid characters."""

    credential: str
    allowed_chars: str


@attrs.define(auto_exc=True, slots=False, init=True)
class AuthStateError(AuthException):
    """A user tried to authenticate multiple Arknights accounts simultaneously."""

    username: str
    """The username of the Duffelbag account."""
    in_progress: bool
    """Whether the authentication was already in progress or not."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagUserExists(AuthException):
    """A new user could not be created because it conflicts with an existing one."""

    username: str
    """The username of the Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagLoginFailure(AuthException):
    """Invalid credentials for a Duffelbag account were provided."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagDeletionAlreadyQueued(AuthException):
    """A user tried to delete a Duffelbag account that is already scheduled for deletion."""

    username: str
    """The username of the Duffelbag account."""
    deletion_ts: datetime.datetime
    """The timestamp at which the Duffelbag account is to be deleted."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagDeletionNotQueued(AuthException):
    """Tried to get a Duffelbag account that is not scheduled for deletion."""


@attrs.define(auto_exc=True, slots=False, init=True)
class DuffelbagConnectionNotFound(AuthException):
    """Could not find a duffelbag account for a given platform account."""

    platform_id: int
    """The user id of the platform account."""
    platform: str
    """The name of the target platform."""


@attrs.define(auto_exc=True, slots=False, init=True)
class PlatformLoginFailure(AuthException):
    """Failed to login to a Duffelbag account by means of a provided platform account."""

    platform: str
    """The name of the target platform."""


@attrs.define(auto_exc=True, slots=False, init=True)
class PlatformConnectionExists(AuthException):
    """Attempted to connect the same external account to two different Duffelbag accounts."""

    username: str
    """The username of the Duffelbag account."""
    existing_username: str
    """The username of the existing Duffelbag account."""
    is_own: bool
    """Whether the platform account is registered to the same Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class PlatformConnectionNotFound(AuthException):
    """Could not find a connected account for a given Duffelbag account."""

    username: str
    """The username of the Duffelbag account."""
    platform: str
    """The name of the target platform."""


@attrs.define(auto_exc=True, slots=False, init=True)
class ArknightsConnectionExists(AuthException):
    """Attempted to connect the same Arknights account to two different Duffelbag accounts."""

    username: str
    """The username of the Duffelbag account that made the request."""
    existing_username: str
    """The username of the existing Duffelbag account."""
    email: str
    """The email address of the existing Arknights account."""
    is_own: bool
    """Whether the Arknights account is registered to the same Duffelbag account."""


@attrs.define(auto_exc=True, slots=False, init=True)
class InvalidEmail(AuthException):
    """Attempted to bind an Arknights account with an invalid email address."""

    email: str
    """The invalid email address."""

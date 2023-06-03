# pyright: reportPrivateUsage = false

"""Functions to do with user authentication for all account types."""

import asyncio
import enum
import re
import typing

import argon2
import arkprts
import asyncpg

import database
from duffelbag import exceptions

# Ensure passwords are hashed at the correct length. Should be 32 chars.
_HASHER = argon2.PasswordHasher(hash_len=32)
MIN_PASS_LEN = 8
MAX_PASS_LEN = 32
MIN_USER_LEN = 4
MAX_USER_LEN = 32

USER_PATTERN = re.compile(r"[a-zA-Z0-9\-_]{4,32}")


class Platform(enum.Enum):
    """External platforms supported by Duffelbag."""

    DISCORD = "Discord"
    ELUDRIS = "Eludris"


class _YostarAuthenticator:
    __slots__: typing.Sequence[str] = ("client", "email")

    client: arkprts.Client
    email: str | None

    def __init__(self, *, client: arkprts.Client | None = None) -> None:
        self.client = client if client else arkprts.Client(pure=True)
        self.email = None

    async def login_with_email(self, email: str, /) -> None:
        if self.email:
            msg = "An email has already been sent."
            raise RuntimeError(msg)

        await self.client._request_yostar_auth(email)

        self.email = email

    async def complete_login(self, verification_code: str) -> tuple[str, str]:
        if not self.email:
            msg = "A verification email must be sent first."
            raise RuntimeError(msg)

        uid, token = await self.client._submit_yostar_auth(self.email, verification_code)
        return await self.client._get_yostar_token(self.email, uid, token)


# NOTE:
# - Key: DuffelbagUser.id
# - Value: (_YostarAuthenticator, authentication timeout task)
_active_authenticators: dict[int, tuple[_YostarAuthenticator, asyncio.Task[None]]] = {}


async def _timeout(key: int, delay: float) -> None:
    await asyncio.sleep(delay)
    _active_authenticators.pop(key)


def _start_timeout(key: int, delay: float = 300.0) -> tuple[float, asyncio.Task[None]]:
    timeout_task = asyncio.create_task(_timeout(key, delay))
    return (delay, timeout_task)


# database.DuffelbagUser manipulation...


def _ensure_valid_pass(password: str) -> None:
    if not MAX_PASS_LEN >= len(password) >= MIN_PASS_LEN:
        msg = f"Passwords must be between {MIN_PASS_LEN} and {MAX_PASS_LEN} characters in length."
        raise ValueError(msg)


def _ensure_valid_user(username: str) -> None:
    if not MAX_USER_LEN >= len(username) >= MIN_USER_LEN:
        msg = f"Usernames must be between {MIN_USER_LEN} and {MAX_USER_LEN} characters in length."
        raise ValueError(msg)

    if not USER_PATTERN.fullmatch(username):
        msg = "Usernames must only contain alphanumerical characters, dashes and underscores."
        raise ValueError(msg)


async def create_user(
    *,
    username: str,
    password: str,
    platform: Platform,
    platform_id: int,
) -> database.DuffelbagUser:
    """Create a new Duffelbag account in the context of an external platform.

    This also creates the corresponding external platform account. Passwords
    are saved as argon2 hashes.

    Parameters
    ----------
    username:
        The username of the Duffelbag account that is to be created.
    password:
        The password of the Duffelbag account that is to be created.
    platform:
        The platform of the account to register.
    platform_id:
        The id of the account on the provided platform.

    Returns
    -------
    :class:`database.DuffelbagUser`
        The newly created Duffelbag user account.

    Raises
    ------
    :class:`ValueError`
        The provided username or password is too short or too long, or the
        username contains invalid characters.
    :class:`exceptions.UserExists`
        A Duffelbag user with the provided name already exists.
    :class:`exceptions.DuplicateUser`
        The external account is already registered to a different Duffelbag
        account. In this case, the new Duffelbag account is NOT created.
    """
    _ensure_valid_user(username)
    _ensure_valid_pass(password)

    hashed = _HASHER.hash(password)

    db = database.get_db_from_table(database.DuffelbagUser)
    new_user = database.DuffelbagUser(username=username, password=hashed)

    async with db.transaction():
        try:
            await database.DuffelbagUser.insert(new_user)

        except asyncpg.UniqueViolationError as exc:
            msg = f"A user named {username!r} already exists. Please try another username."
            raise exceptions.UserExists(msg, duffelbag_user=new_user) from exc

        else:
            # NOTE: If this raises, the transaction is automatically rolled back.
            await add_platform_account(new_user, platform=platform, platform_id=platform_id)

            return new_user


async def login_user(*, username: str, password: str) -> database.DuffelbagUser:
    """Log in to an existing Duffelbag user account and return it.

    Parameters
    ----------
    username:
        The username of the Duffelbag account.
    password:
        The password of the Duffelbag account.

    Returns
    -------
    :class:`database.DuffelbagUser`
        The Duffelbag user account with the provided username and password.

    Raises
    ------
    :class:`ValueError`
        The provided username or password is too short or too long, or the
        username contains invalid characters.
    :class:`exceptions.UserNotFound`
        No Duffelbag user with the provided username exists.
    :class:`exceptions.InvalidPassword`
        The provided password was incorrect.
    """
    _ensure_valid_user(username)
    _ensure_valid_pass(password)

    # Due to the unique constraint on DuffelbagUser.username, it's safe to only
    # return the fist object.
    user = await (
        database.DuffelbagUser.objects()
        .where(database.DuffelbagUser.username == username)
        .first()
    )  # fmt: skip

    if not user:
        msg = f"No Duffelbag user named {username!r} exists."
        raise exceptions.UserNotFound(msg)

    try:
        _HASHER.verify(user.password, password)

    except argon2.exceptions.VerifyMismatchError as exc:
        msg = f"The password entered for Duffelbag account {username!r} is incorrect."
        raise exceptions.InvalidPassword(msg) from exc

    else:
        return user


async def delete_user(*, username: str, password: str) -> None:
    """Remove an existing Duffelbag account and all related user information.

    Parameters
    ----------
    username:
        The username of the Duffelbag account.
    password:
        The password of the Duffelbag account.

    Raises
    ------
    :class:`ValueError`
        The provided username or password is too short or too long, or the
        username contains invalid characters.
    :class:`exceptions.UserNotFound`
        No Duffelbag user with the provided username exists.
    :class:`exceptions.InvalidPassword`
        The provided password was incorrect.
    """
    user = await login_user(username=username, password=password)
    await user.remove()


async def recover_user(
    *, platform: Platform, platform_id: int, password: str
) -> database.DuffelbagUser:
    """Recover an existing Duffelbag account through a connected external platform account.

    This updates the password of the connected account to the newly provided
    password.

    Parameters
    ----------
    platform:
        The external platform with which to recover a Duffelbag account.
    platform_id:
        The id of the account on the provided platform.
    password:
        The new password to use for the connected Duffelbag account.

    Returns
    -------
    :class:`database.DuffelbagUser`
        The Duffelbag account connected to the provided external platform
        account.

    Raises
    ------
    :class:`ValueError`
        The provided username or password is too short or too long, or the
        username contains invalid characters.
    :class:`exceptions.UserNotFound`
        The external account is not registered to any existing Duffelbag
        account.
    """
    _ensure_valid_pass(password)

    joined = database.DuffelbagUser.id.join_on(database.PlatformUser.user)

    duffelbag_user = await (
        database.DuffelbagUser.objects()
        .where((joined.platform_id == platform_id) & (joined.platform_name == platform.name))
        .first()
    )  # fmt: skip

    if not duffelbag_user:
        msg = (
            f"External platform account with id '{platform_id}' on platform"
            f" {platform.name!r} is not bound to any Duffelbag account."
        )
        raise exceptions.UserNotFound(msg)

    # Update password.
    duffelbag_user.password = _HASHER.hash(password)
    await duffelbag_user.save(  # pyright: ignore[reportUnknownMemberType]
        [database.DuffelbagUser.password]
    )

    return duffelbag_user


# database.PlatformUser manipulation...


async def add_platform_account(
    duffelbag_user: database.DuffelbagUser, *, platform: Platform, platform_id: int
) -> database.PlatformUser:
    """Add a platform account to an existing Duffelbag account.

    Parameters
    ----------
    duffelbag_user:
        An existing Duffelbag account. This should be acquired using
        :func:`login_user`.
    platform:
        The platform of the account to register.
    platform_id:
        The id of the account on the provided platform.

    Returns
    -------
    :class:`database.PlatformUser`
        The external account that was just registered.

    Raises
    ------
    :class:`exceptions.DuplicateUser`
        The external account is already registered to a different Duffelbag
        account.
    """
    platform_user = database.PlatformUser(
        user=duffelbag_user.id,
        platform_id=platform_id,
        platform_name=platform.name,
    )

    try:
        await database.PlatformUser.insert(platform_user)

    except asyncpg.UniqueViolationError as exc:
        msg = (
            f"External platform account with id '{platform_id}' on platform"
            f" {platform.name!r} is already registered to a Duffelbag account."
        )
        raise exceptions.DuplicateUser(
            msg,
            duffelbag_user=duffelbag_user,
            account=platform_user,
        ) from exc

    else:
        return platform_user


async def remove_platform_account(
    duffelbag_user: database.DuffelbagUser, *, platform: Platform, platform_id: int
) -> None:
    """Remove a platform account from an existing Duffelbag account.

    Parameters
    ----------
    duffelbag_user:
        An existing Duffelbag account. This should be acquired using
        :func:`login_user`.
    platform:
        The platform of the account to deregister.
    platform_id:
        The id of the account on the provided platform.

    Raises
    ------
    :class:`exceptions.UserNotFound`
        The external account is not registered to the provided Duffelbag
        account.
    """
    result: list[dict[str, object]] = await (
        database.PlatformUser.delete()
        .where(
            (database.PlatformUser.user == duffelbag_user.id)
            & (database.PlatformUser.platform_id == platform_id)
            & (database.PlatformUser.platform_name == platform.name)
        )
        .returning(database.PlatformUser.id)
    )

    if result:
        return

    msg = (
        f"No external platform account with id '{platform_id}' on platform"
        f" {platform.name!r} is registered to the Duffelbag account with"
        f" username {duffelbag_user.username!r} and ID '{duffelbag_user.id}'."
    )
    raise exceptions.UserNotFound(msg)


async def list_connected_accounts(
    duffelbag_user: database.DuffelbagUser,
) -> typing.Sequence[database.PlatformUser]:
    """Return all external platform accounts connected to the provided Duffelbag account.

    Parameters
    ----------
    duffelbag_user:
        An existing Duffelbag account. This should be acquired using
        :func:`login_user`.

    Returns
    -------
    Sequence[:class:`database.PlatformUser`]
        All external platform accounts connected to the provided Duffelbag
        account.
    """
    return await (
        database.PlatformUser.objects()
        .where(database.PlatformUser.user == duffelbag_user.id)
    )  # fmt: skip


# database.ArknightsUser manipulation...


async def start_authentication(
    duffelbag_user: database.DuffelbagUser, *, email: str
) -> tuple[float, asyncio.Task[None]]:
    """Start the authentication process to register a new Arknights account to a Duffelbag account.

    As a result of running this function, a verification email will be sent to
    the provided email address. The verification process needs to be completed
    by calling :func:`complete_authentication` with the verification code
    provided in the received email.

    Parameters
    ----------
    duffelbag_user:
        The duffelbag account to which to register the Arknights account.
    email:
        The email address of the Arknights account that is to be registered.
        A verification email will be sent to this email address.

    Returns
    -------
    tuple[:class:`float`, :class:`asyncio.Task`[None]]
        A tuple with the timeout duration and the timeout task. The task can be
        awaited to wait for the full timeout.

    Raises
    ------
    :class:`exceptions.DuplicateUser`:
        The email address is already registered to a Duffelbag account. This
        prevents the verification mail from being sent unnecessarily. Note that
        this can only occur if the user opted to store their email address.
    :class:`exceptions.AlreadyAuthenticating`:
        The user already has an ongoing authentication process.
    """
    existing_user = await (
        database.ArknightsUser.objects()
        .where(database.ArknightsUser.email == email)
        .first()
    )  # fmt: skip
    if existing_user:
        msg = (
            f"The arknights account with email address {email!r} is already"
            " registered to a Duffelbag user."
        )
        raise exceptions.DuplicateUser(msg, duffelbag_user=duffelbag_user, account=existing_user)

    if duffelbag_user.id in _active_authenticators:
        msg = f"Duffelbag user {duffelbag_user.username!r} is already undergoing authentication."
        raise exceptions.AlreadyAuthenticating(msg, duffelbag_user=duffelbag_user, email=email)

    authenticator = _YostarAuthenticator()
    await authenticator.login_with_email(email)

    delay, timeout_task = _start_timeout(duffelbag_user.id)
    _active_authenticators[duffelbag_user.id] = (authenticator, timeout_task)

    return delay, timeout_task


async def complete_authentication(
    duffelbag_user: database.DuffelbagUser,
    *,
    verification_code: str,
    store_email: bool = False,
) -> database.ArknightsUser:
    """Complete the authentication process started by :func:`start_authentication`.

    This requires the verification code sent to the email address that was
    provided to :func:`start_authentication`.

    Parameters
    ----------
    duffelbag_user:
        The duffelbag account to which to register the Arknights account.
    verification_code:
        The verification code that was emailed to the email address that was
        provided to :func:`start_authentication`.
    store_email:
        Whether or not to store the email address for this Arknights account.
        This serves to make it easier to recognise stored accounts and to
        prevent accidentally trying to double-register the same account.
        Defaults to ``False`` to accommodate user privacy.

    Raises
    ------
    :class:`exceptions.NotAuthenticating`:
        The provided Duffelbag account is not currently undergoing an
        authentication process.
    """
    if duffelbag_user.id not in _active_authenticators:
        msg = (
            f"Duffelbag user {duffelbag_user.username!r} is not in an active"
            " authentication process."
        )
        raise exceptions.NotAuthenticating(msg, duffelbag_user=duffelbag_user)

    authenticator, timeout_task = _active_authenticators.pop(duffelbag_user.id)

    if not timeout_task.done() and not timeout_task.cancelled():
        timeout_task.cancel()

    uid, token = await authenticator.complete_login(verification_code)

    return await add_arknights_account(
        duffelbag_user,
        uid=uid,
        token=token,
        email=authenticator.email if store_email else None,
    )


async def add_arknights_account(
    duffelbag_user: database.DuffelbagUser,
    *,
    uid: str,
    token: str,
    email: str | None = None,
) -> database.ArknightsUser:
    """Add an Arknights account to an existing Duffelbag account.

    Parameters
    ----------
    duffelbag_user:
        An existing Duffelbag account. This should be acquired using
        :func:`login_user`.
    uid:
        The Arknights channel uid for account that is to be added.
    token:
        The Yostar token for the account that is to be added.
    email:
        The email address to register to the account. To accommodate user
        privacy, this is left optional.

    Returns
    -------
    :class:`database.ArknightsUser`
        The Arknights account that was just registered.

    Raises
    ------
    :class:`exceptions.DuplicateUser`
        The external account is already registered to a different Duffelbag
        account.
    """
    new_user = database.ArknightsUser(
        user=duffelbag_user.id,
        channel_uid=uid,
        yostar_token=token,
        email=email,
    )

    try:
        await database.ArknightsUser.insert(new_user)

    except asyncpg.UniqueViolationError as exc:
        msg = "This Arknights user is already registered to a different Duffelbag account."
        raise exceptions.DuplicateUser(
            msg,
            duffelbag_user=duffelbag_user,
            account=new_user,
        ) from exc

    else:
        return new_user


async def remove_arknights_account() -> typing.NoReturn:
    """Remove an arknights account from the provided Duffelbag account."""
    # TODO: Figure out how to implement this. Either we need to make emails
    #       required, or we'd need to loop over every account, fetch the ingame
    #       username, and use that instead?
    #       Either way, we need some way for the user to tell which account is
    #       theirs.

    raise NotImplementedError


async def list_arknights_accounts(
    duffelbag_user: database.DuffelbagUser,
) -> typing.Sequence[database.ArknightsUser]:
    """Return all Arknights accounts connected to the provided Duffelbag account.

    Parameters
    ----------
    duffelbag_user:
        An existing Duffelbag account. This should be acquired using
        :func:`login_user`.

    Returns
    -------
    Sequence[:class:`database.PlatformUser`]
        All Arknights accounts connected to the provided Duffelbag account.
    """
    return await (
        database.ArknightsUser.objects()
        .where(database.ArknightsUser.user == duffelbag_user.id)
    )  # fmt: skip

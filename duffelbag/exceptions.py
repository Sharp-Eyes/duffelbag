"""Module containing exceptions raised by the Duffelbag bot."""

import database


class DuffelbagException(Exception):
    """Base exception class for exceptions raised by Duffelbag."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message

        super().__init__(message, *args)


class AuthException(DuffelbagException):
    """Base exception class for exceptions raised as part of authentication."""


class AlreadyAuthenticating(AuthException):
    """A user tried to authenticate multiple Arknights accounts simultaneously."""

    def __init__(
        self,
        message: str,
        *,
        duffelbag_user: database.DuffelbagUser,
        email: str,
    ) -> None:
        self.message = message
        self.duffelbag_user = duffelbag_user
        self.email = email

        super().__init__(message, duffelbag_user, email)


class NotAuthenticating(AuthException):
    """A user tried to complete Arknights account authentication without starting it."""

    def __init__(
        self,
        message: str,
        *,
        duffelbag_user: database.DuffelbagUser,
    ) -> None:
        self.message = message
        self.duffelbag_user = duffelbag_user

        super().__init__(message, duffelbag_user)


class UserExists(AuthException):
    """A new user could not be created because it conflicts with an existing one."""

    def __init__(
        self,
        message: str,
        *,
        duffelbag_user: database.DuffelbagUser,
    ) -> None:
        self.message = message
        self.duffelbag_user = duffelbag_user

        super().__init__(message, duffelbag_user)


class UserNotFound(AuthException):
    """A user could not be retrieved because the provided data do not match an existing user."""


class InvalidPassword(AuthException):
    """The provided password was invalid."""


class DuplicateUser(AuthException):
    """An attempt was made to link the same user to two different accounts."""

    def __init__(
        self,
        message: str,
        *,
        duffelbag_user: database.DuffelbagUser,
        account: database.PlatformUser | database.ArknightsUser,
    ) -> None:
        self.message = message
        self.duffelbag_user = duffelbag_user
        self.account = account

        super().__init__(message, duffelbag_user, account)

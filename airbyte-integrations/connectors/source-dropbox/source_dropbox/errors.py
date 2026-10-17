# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from dropbox.exceptions import AuthError, BadInputError


class DropboxAuthenticationError(RuntimeError):
    """Raised when the base Dropbox credentials are invalid, revoked, or insufficient."""


class DropboxRateLimitError(RuntimeError):
    """Raised only after the Dropbox SDK exhausts its rate-limit retries."""


class DropboxCursorResetError(RuntimeError):
    """Raised when Dropbox invalidates a list-folder cursor."""


class DropboxSharingPermissionError(RuntimeError):
    """Raised when the Dropbox app cannot read sharing metadata."""


class DropboxSharingAclError(RuntimeError):
    """Raised when Dropbox shared-folder ACLs cannot be inventoried safely."""


class DropboxSharedLinksCursorResetError(RuntimeError):
    """Raised when Dropbox repeatedly invalidates a shared-links cursor."""


class DropboxSharedFoldersCursorResetError(RuntimeError):
    """Raised when Dropbox repeatedly invalidates a shared-folders cursor."""


class DropboxFilePropertiesError(RuntimeError):
    """Raised when Dropbox File Properties cannot be listed safely."""


class DropboxNamespaceError(RuntimeError):
    """Raised when Dropbox Business namespaces cannot be resolved safely."""


def raise_auth_or_refresh_error(exc: AuthError | BadInputError, *, required_scope: str | None = None) -> None:
    """Raise user-actionable credential errors at every Dropbox SDK boundary.

    Missing optional scopes are intentionally local to the stream that needs them.
    Refresh failures, including ones raised after connection checking, are always
    reported as connection credential failures rather than raw SDK exceptions.
    """
    if required_scope and _is_missing_scope_error(exc, required_scope):
        if required_scope == "sharing.read":
            raise DropboxSharingPermissionError("Dropbox app requires sharing.read to sync sharing streams.") from exc
    message = _authentication_message(exc) if isinstance(exc, AuthError) else _token_exchange_message(exc)
    raise DropboxAuthenticationError(message) from exc


def _authentication_message(exc: AuthError) -> str:
    tag = getattr(exc.error, "_tag", None)
    if tag == "missing_scope":
        return "Dropbox credentials are valid but missing a required base scope (account_info.read or files.metadata.read)."
    if tag in {"invalid_access_token", "expired_access_token"}:
        return "Dropbox refresh token or access token is invalid, expired, or revoked. Re-authorize the app."
    return "Dropbox rejected the supplied credentials. Check the app key and refresh token."


def _token_exchange_message(exc: BadInputError) -> str:
    message = exc.message.lower()
    if "invalid_client" in message:
        return "Dropbox rejected the app key. Check the configured Dropbox app key."
    if "invalid_grant" in message:
        return "Dropbox rejected the refresh token. It may be invalid or revoked; re-authorize the app."
    return "Dropbox could not refresh the access token. Check the app key and refresh token."


def _is_missing_scope_error(exc: AuthError | BadInputError, required_scope: str) -> bool:
    """Recognize both structured and plaintext missing-scope SDK responses.

    Some Dropbox endpoints return a HTTP 400 plaintext response. The SDK
    exposes that response as ``BadInputError`` rather than the usual structured
    ``AuthError(missing_scope)``.
    """
    if isinstance(exc, AuthError):
        return getattr(exc.error, "_tag", None) == "missing_scope"
    message = exc.message.lower()
    return "required scope" in message and required_scope.lower() in message

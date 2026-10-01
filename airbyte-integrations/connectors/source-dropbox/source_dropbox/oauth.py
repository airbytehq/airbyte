"""Small, headless PKCE setup helper for the Dropbox source."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


AUTHORIZE_URL = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"

CORE_SCOPES = ("account_info.read", "files.metadata.read")
SHARING_SCOPE = "sharing.read"
SCOPE_PRESETS = {
    "core": CORE_SCOPES,
    "core+sharing": (*CORE_SCOPES, SHARING_SCOPE),
}
DEFAULT_SCOPE_PRESET = "core+sharing"


class DropboxOAuthError(RuntimeError):
    """A user-actionable failure while obtaining a refresh token."""


@dataclass(frozen=True)
class PkceCodes:
    verifier: str
    challenge: str


def generate_pkce_codes() -> PkceCodes:
    """Generate RFC 7636-compliant PKCE verifier and S256 challenge."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    return PkceCodes(verifier=verifier, challenge=challenge)


def authorization_url(app_key: str, codes: PkceCodes, scopes: Sequence[str]) -> str:
    """Build the Dropbox URL for a headless authorization-code flow."""
    params = {
        "client_id": app_key,
        "response_type": "code",
        "token_access_type": "offline",
        "code_challenge_method": "S256",
        "code_challenge": codes.challenge,
        "scope": " ".join(scopes),
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(
    app_key: str,
    authorization_code: str,
    verifier: str,
    *,
    request: Callable[[Request], tuple[int, bytes]] | None = None,
) -> str:
    """Exchange a Dropbox authorization code for a refresh token using PKCE."""
    body = urlencode(
        {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "client_id": app_key,
            "code_verifier": verifier,
        }
    ).encode("ascii")
    token_request = Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        status, payload = request(token_request) if request else _post(token_request)
    except HTTPError as exc:
        status, payload = exc.code, exc.read()
    except URLError as exc:
        raise DropboxOAuthError(f"Could not reach Dropbox OAuth: {exc.reason}") from exc

    try:
        response = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DropboxOAuthError("Dropbox OAuth returned an invalid response.") from exc
    if status >= 400:
        raise DropboxOAuthError(_oauth_error_message(response))
    refresh_token = response.get("refresh_token")
    if not isinstance(refresh_token, str) or not refresh_token:
        raise DropboxOAuthError("Dropbox did not return a refresh token. Ensure offline access was requested.")
    return refresh_token


def _post(request: Request) -> tuple[int, bytes]:
    with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed Dropbox endpoint
        return response.status, response.read()


def _oauth_error_message(response: dict[str, Any]) -> str:
    error = response.get("error")
    description = response.get("error_description")
    if error == "invalid_client":
        return "Dropbox rejected the app key. Check --app-key and the Dropbox app configuration."
    if error == "invalid_grant":
        return "The authorization code is invalid, expired, or already used. Run authorize again."
    detail = description if isinstance(description, str) else error
    return f"Dropbox OAuth failed{f': {detail}' if detail else ''}."


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create Dropbox refresh-token credentials for Airbyte.")
    commands = parser.add_subparsers(dest="command", required=True)
    authorize = commands.add_parser("authorize", help="Authorize Dropbox with PKCE and print Airbyte credentials JSON.")
    authorize.add_argument("--app-key", required=True, help="Dropbox app key from the App Console.")
    authorize.add_argument(
        "--scope-preset",
        choices=tuple(SCOPE_PRESETS),
        default=DEFAULT_SCOPE_PRESET,
        help="Permission set to request (default: core+sharing).",
    )
    return parser


def main(argv: Sequence[str] | None = None, *, input_fn: Callable[[str], str] = input) -> int:
    args = _parser().parse_args(argv)
    if args.command != "authorize":  # pragma: no cover - argparse enforces this.
        return 2
    app_key = args.app_key.strip()
    if not app_key:
        raise DropboxOAuthError("Dropbox app key cannot be empty.")
    codes = generate_pkce_codes()
    scopes = SCOPE_PRESETS[args.scope_preset]
    print("Open this URL in a browser and approve the Dropbox app:\n")
    print(authorization_url(app_key, codes, scopes))
    print("\nDropbox will display an authorization code. Paste it below.")
    code = input_fn("Authorization code: ").strip()
    if not code:
        raise DropboxOAuthError("Authorization code cannot be empty.")
    refresh_token = exchange_code(app_key, code, codes.verifier)
    print("\nPaste this JSON into the Airbyte Dropbox connector configuration:\n")
    credentials = {
        "credentials": {
            "auth_type": "oauth2_pkce",
            "app_key": app_key,
            "refresh_token": refresh_token,
        }
    }
    print(json.dumps(credentials, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DropboxOAuthError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

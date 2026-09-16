# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-gong`'s OAuth refresh request shape.

Gong's documented OAuth refresh endpoint expects `grant_type` and `refresh_token`
on the URL **query string**, with credentials passed via `Authorization: Basic ...`.
This test verifies the connector's manifest configures the `OAuthAuthenticator`
with `send_refresh_request_as_query_params: true` so the CDK routes the standard
OAuth refresh args to the URL query string instead of the request body.

See: <https://gong.app.gong.io/settings/api/documentation#section/Authentication/OAuth-2.0>
"""

from pathlib import Path

import yaml


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _oauth_authenticator_block() -> dict:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return manifest["definitions"]["base_requester"]["authenticator"]["authenticators"]["OAuth2.0"]


def test_oauth_authenticator_sends_refresh_request_as_query_params():
    """The OAuth authenticator opts into the URL-query-string refresh shape so
    the refresh request hits Gong's documented URL shape.
    """
    oauth = _oauth_authenticator_block()
    assert oauth["type"] == "OAuthAuthenticator"
    assert oauth.get("send_refresh_request_as_query_params") is True


def test_oauth_authenticator_keeps_basic_auth_header():
    """The OAuth authenticator continues to send credentials via the
    `Authorization: Basic ...` header, matching Gong's documented requirement.
    """
    oauth = _oauth_authenticator_block()
    headers = oauth.get("refresh_request_headers") or {}
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")

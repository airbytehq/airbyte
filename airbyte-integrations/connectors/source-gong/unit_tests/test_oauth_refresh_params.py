# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-gong`'s OAuth refresh request shape.

Gong's documented OAuth refresh endpoint expects `grant_type` and `refresh_token`
on the URL **query string**, with credentials passed via `Authorization: Basic ...`.
This test verifies the connector's manifest configures the `OAuthAuthenticator`
with `refresh_request_query_params` containing the right values.

See: <https://gong.app.gong.io/settings/api/documentation#section/Authentication/OAuth-2.0>
"""

from pathlib import Path

import yaml


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _oauth_authenticator_block() -> dict:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return manifest["definitions"]["base_requester"]["authenticator"]["authenticators"]["OAuth2.0"]


def test_oauth_authenticator_has_refresh_request_query_params():
    """The OAuth authenticator declares `refresh_request_query_params` with
    `grant_type` and `refresh_token` so the refresh request hits Gong's
    documented URL shape.
    """
    oauth = _oauth_authenticator_block()
    assert oauth["type"] == "OAuthAuthenticator"
    assert oauth.get("refresh_request_query_params") == {
        "grant_type": "refresh_token",
        "refresh_token": "{{ config['credentials']['refresh_token'] }}",
    }


def test_oauth_authenticator_keeps_basic_auth_header():
    """The OAuth authenticator continues to send credentials via the
    `Authorization: Basic ...` header, matching Gong's documented requirement.
    """
    oauth = _oauth_authenticator_block()
    headers = oauth.get("refresh_request_headers") or {}
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")

# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import hashlib
import json
from urllib.parse import parse_qs, urlparse

import pytest
from source_dropbox.oauth import (
    DEFAULT_SCOPE_PRESET,
    SCOPE_PRESETS,
    DropboxOAuthError,
    PkceCodes,
    authorization_url,
    exchange_code,
    generate_pkce_codes,
    main,
)


def test_pkce_codes_are_s256_and_rfc7636_length() -> None:
    codes = generate_pkce_codes()

    assert 43 <= len(codes.verifier) <= 128
    expected = base64.urlsafe_b64encode(hashlib.sha256(codes.verifier.encode()).digest()).rstrip(b"=").decode()
    assert codes.challenge == expected


def test_authorization_url_requests_offline_access_and_selected_scopes() -> None:
    url = authorization_url("app-key", PkceCodes("a" * 43, "challenge"), SCOPE_PRESETS[DEFAULT_SCOPE_PRESET])
    params = parse_qs(urlparse(url).query)

    assert params["client_id"] == ["app-key"]
    assert params["token_access_type"] == ["offline"]
    assert params["code_challenge_method"] == ["S256"]
    assert params["scope"] == ["account_info.read files.metadata.read sharing.read"]
    assert "redirect_uri" not in params


def test_exchange_code_returns_refresh_token_and_uses_verifier() -> None:
    captured = {}

    def request(request):
        captured["body"] = request.data.decode()
        return 200, b'{"refresh_token":"refresh"}'

    assert exchange_code("app-key", "code", "verifier", request=request) == "refresh"
    assert parse_qs(captured["body"]) == {
        "code": ["code"],
        "grant_type": ["authorization_code"],
        "client_id": ["app-key"],
        "code_verifier": ["verifier"],
    }


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"error": "invalid_client"}, "app key"),
        ({"error": "invalid_grant"}, "invalid, expired, or already used"),
    ],
)
def test_exchange_code_classifies_oauth_failures(payload, message) -> None:
    with pytest.raises(DropboxOAuthError, match=message):
        exchange_code("app-key", "code", "verifier", request=lambda _: (400, json.dumps(payload).encode()))


def test_authorize_command_prints_airbyte_credentials(monkeypatch, capsys) -> None:
    monkeypatch.setattr("source_dropbox.oauth.generate_pkce_codes", lambda: PkceCodes("v" * 43, "challenge"))
    monkeypatch.setattr("source_dropbox.oauth.exchange_code", lambda *_: "refresh")

    assert (
        main(
            ["authorize", "--app-key", "app-key", "--scope-preset", "core"],
            input_fn=lambda _: "code",
        )
        == 0
    )
    output = capsys.readouterr().out
    assert '"auth_type": "oauth2_pkce"' in output
    assert '"refresh_token": "refresh"' in output

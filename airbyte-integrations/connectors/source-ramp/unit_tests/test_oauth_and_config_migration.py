# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-ramp` authentication options and the config migration that introduced them:

- the OAuth option logs in with the `refresh_token` grant, HTTP Basic client credentials, and no scope
- configs created before OAuth support (flat `client_id` / `client_secret`) are migrated into the
  client-credentials option and keep reading
- `spec.advanced_auth` requests the same scopes the client-credentials login does
"""

import base64
import json
import logging
from urllib.parse import parse_qs

import requests_mock
from _helpers import (
    ACCESS_TOKEN,
    ALL_SCOPES,
    CONFIG,
    LEGACY_CONFIG,
    OAUTH_CONFIG,
    TOKEN_RESPONSE,
    TOKEN_URL,
    TRANSACTIONS_URL,
    get_source,
    read_stream,
    record_ids,
    requests_to,
)

from airbyte_cdk.models import FailureType


TOKEN_PATH = "/developer/v1/token"
TRANSACTIONS_PATH = "/developer/v1/transactions"

OAUTH_TOKEN_RESPONSE = {"access_token": ACCESS_TOKEN, "expires_in": 3600, "token_type": "Bearer"}


def _transactions_page() -> dict:
    return {"data": [{"id": "tx-1", "updated_at": "2024-06-01T00:00:00+00:00"}], "page": {"next": None}}


def _basic_credentials(request) -> str:
    authorization = request.headers["Authorization"]
    assert authorization.startswith("Basic "), f"login must use HTTP Basic auth, got {authorization!r}"
    return base64.b64decode(authorization.removeprefix("Basic ")).decode()


def test_oauth_login_uses_refresh_token_grant():
    """The OAuth option exchanges the stored refresh token, authenticating the app with HTTP Basic."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=OAUTH_TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_transactions_page())
        output = read_stream("transactions", config=OAUTH_CONFIG)

    assert record_ids(output) == ["tx-1"]

    token_requests = requests_to(mocker.request_history, TOKEN_PATH)
    assert len(token_requests) == 1, f"expected exactly one login request, got {len(token_requests)}"
    login = token_requests[0]
    credentials = OAUTH_CONFIG["credentials"]
    assert _basic_credentials(login) == f"{credentials['client_id']}:{credentials['client_secret']}"

    form_body = parse_qs(login.text)
    assert form_body == {"grant_type": ["refresh_token"], "refresh_token": [credentials["refresh_token"]]}, (
        f"unexpected OAuth login form {form_body}"
    )

    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert data_requests[0].headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_oauth_login_error_asks_to_reauthenticate():
    """An expired or revoked refresh token fails as `config_error`, quotes Ramp's reason and asks to re-authenticate."""
    body = {"error": "invalid_grant", "error_description": "Refresh token is expired"}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=body, status_code=400)
        output = read_stream("transactions", config=OAUTH_CONFIG)

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, f"expected config_error, got {errors[0].failure_type}"
    assert "Re-authenticate the source" in errors[0].message, f"unexpected message {errors[0].message!r}"
    assert "(Refresh token is expired)" in errors[0].message, f"unexpected message {errors[0].message!r}"
    assert "client secret" not in errors[0].message, f"OAuth users have no client secret to fix: {errors[0].message!r}"


def test_legacy_config_is_migrated_to_client_credentials(tmp_path):
    """A flat pre-OAuth config is rewritten into the client-credentials option, with the flat fields removed."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(LEGACY_CONFIG))

    get_source(LEGACY_CONFIG, config_path=str(config_path))

    assert json.loads(config_path.read_text()) == CONFIG


def test_migration_leaves_current_configs_untouched(tmp_path):
    """Configs already in the `credentials` shape, of either option, are not rewritten."""
    for config in (CONFIG, OAUTH_CONFIG):
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        get_source(config, config_path=str(config_path))

        assert json.loads(config_path.read_text()) == config


def test_legacy_config_still_reads():
    """A connection still on the flat config keeps logging in with its client credentials."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_transactions_page())
        output = read_stream("transactions", config=LEGACY_CONFIG)

    assert record_ids(output) == ["tx-1"]
    login = requests_to(mocker.request_history, TOKEN_PATH)[0]
    assert _basic_credentials(login) == f"{LEGACY_CONFIG['client_id']}:{LEGACY_CONFIG['client_secret']}"
    assert parse_qs(login.text) == {"grant_type": ["client_credentials"], "scope": [ALL_SCOPES]}


def test_advanced_auth_requests_the_client_credentials_scopes():
    """The OAuth consent asks for every stream's scope, exactly as the client-credentials login does."""
    spec = get_source(CONFIG).spec(logging.getLogger("test_advanced_auth"))
    advanced_auth = spec.advanced_auth

    assert advanced_auth.predicate_key == ["credentials", "auth_type"]
    assert advanced_auth.predicate_value == "oauth2.0"
    connector_input = advanced_auth.oauth_config_specification.oauth_connector_input_specification
    assert connector_input.scope == ALL_SCOPES

    oauth_option = spec.connectionSpecification["properties"]["credentials"]["oneOf"][0]
    assert oauth_option["properties"]["auth_type"]["const"] == "oauth2.0", "OAuth must be the first option"

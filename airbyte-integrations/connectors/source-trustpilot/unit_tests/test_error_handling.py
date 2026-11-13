# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-trustpilot` HTTP error handling.

Prior to v0.4.13, the connector's three streams ignored HTTP 400/403/404 responses
with `action: IGNORE`, which caused syncs to complete "successfully" with zero records
whenever the Trustpilot API rejected a request (e.g. expired OAuth refresh token).

These tests assert the new behavior: 400/401/403/404 responses now fail the sync
with `failure_type: config_error` so the user sees the real problem.
"""

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


# Use OAuth2.0 credentials to avoid activating the apikey `ApiKeyAuthenticator`
# branch on the shared `base_requester`. The manifest separately sets an
# `apikey` request header on two streams; when the apikey authenticator is also
# active it collides with that header inside the CDK, which masks the HTTP
# error behavior these tests exercise.
_CONFIG = {
    "credentials": {
        "auth_type": "oauth2.0",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "token_expiry_date": "2099-01-01T00:00:00Z",
    },
    "oauth_access_token": "test_access_token",
    "oauth_token_expiry_date": "2099-01-01T00:00:00Z",
    "client_refresh_token": "test_refresh_token",
    "client_id": "test_api_key",
    "start_date": "2024-01-01T00:00:00Z",
    "business_units": ["example.com"],
}

_BUSINESS_UNITS_FIND_URL = "https://api.trustpilot.com/v1/business-units/find"
_BUSINESS_UNITS_ALL_URL = "https://api.trustpilot.com/v1/business-units/all"


def _sync(stream_name: str):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog)


def _config_error_messages(output) -> list[str]:
    assert output.errors, f"expected at least one error trace message, got none. logs: {[m.log.message for m in output.logs if m.log]}"
    messages: list[str] = []
    for error in output.errors:
        if not (error.trace and error.trace.error):
            continue
        if error.trace.error.failure_type != FailureType.config_error:
            continue
        messages.append(error.trace.error.message or "")
    assert messages, (
        "expected at least one config_error trace, got failure_types="
        f"{[e.trace.error.failure_type for e in output.errors if e.trace and e.trace.error]}"
    )
    return messages


@pytest.mark.parametrize(
    "stream_name,mock_url",
    [
        pytest.param("configured_business_units", _BUSINESS_UNITS_FIND_URL, id="configured_business_units"),
        pytest.param("business_units", _BUSINESS_UNITS_ALL_URL, id="business_units"),
    ],
)
@pytest.mark.parametrize(
    "status_code",
    [
        pytest.param(400, id="400_bad_request"),
        pytest.param(401, id="401_unauthorized"),
        pytest.param(403, id="403_forbidden"),
        pytest.param(404, id="404_not_found"),
    ],
)
def test_client_error_responses_fail_with_config_error(stream_name, mock_url, status_code):
    """Streams surface a `config_error` trace on 400/401/403/404 instead of silently returning zero records."""
    with requests_mock.Mocker() as mocker:
        mocker.get(mock_url, status_code=status_code, json={"message": "nope"})
        output = _sync(stream_name)

    _config_error_messages(output)
    assert not output.records, f"expected no records on {status_code} response, got {len(output.records)}"


def test_configured_business_units_404_error_message_mentions_business_units_field():
    """The 404 error on `configured_business_units` names the `business_units` config field so users can self-diagnose."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_BUSINESS_UNITS_FIND_URL, status_code=404, json={"message": "not found"})
        output = _sync("configured_business_units")

    messages = _config_error_messages(output)
    assert any('"business_units"' in msg for msg in messages), (
        f"expected 404 error to mention the business_units config field, got messages={messages}"
    )


def test_configured_business_units_400_error_message_mentions_unauthorized_or_malformed():
    """The 400/401/403 error message surfaces an auth-or-request failure instead of the previous typo'd "Credentails" string."""
    with requests_mock.Mocker() as mocker:
        mocker.get(_BUSINESS_UNITS_FIND_URL, status_code=400, json={"message": "bad request"})
        output = _sync("configured_business_units")

    messages = _config_error_messages(output)
    assert any("unauthorized or malformed" in msg for msg in messages), (
        f"expected 400 error to describe an unauthorized or malformed request, got messages={messages}"
    )
    assert not any("Credentails" in msg for msg in messages), (
        f"did not expect the legacy 'Credentails' typo in error messages, got messages={messages}"
    )

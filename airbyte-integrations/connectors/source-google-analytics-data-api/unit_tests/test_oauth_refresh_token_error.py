#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
import requests_mock

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


_TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
_REFRESH_TOKEN_REJECTED_MESSAGE = "Refresh token was rejected by the OAuth provider"

_CONFIG = {
    "credentials": {
        "auth_type": "Client",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token",
    },
    "date_ranges_start_date": "2025-01-01",
    "date_ranges_end_date": "2025-01-01",
    "property_ids": ["111"],
}


def _read_with_token_response(status_code, body):
    catalog = CatalogBuilder().with_stream("property_metadata", SyncMode.full_refresh).build()
    with requests_mock.Mocker() as http_mocker:
        http_mocker.post(_TOKEN_URL, status_code=status_code, json=body)
        output = read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=True)
    # The sync-level summary trace is always `config_error`, so assert on the stream-level one.
    stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert len(stream_errors) == 1, stream_errors
    return stream_errors[0]


@pytest.mark.parametrize("status_code", [400, 401])
@pytest.mark.parametrize("error_code", ["invalid_grant", "invalid_client", "unauthorized_client"])
def test_rejected_refresh_token_is_config_error(status_code, error_code):
    error = _read_with_token_response(status_code, {"error": error_code, "error_description": "Token has been expired or revoked."})

    assert error.failure_type == FailureType.config_error
    assert _REFRESH_TOKEN_REJECTED_MESSAGE in error.message


def test_unrelated_token_error_is_not_reported_as_expired_refresh_token():
    error = _read_with_token_response(400, {"error": "invalid_request"})

    assert error.failure_type == FailureType.system_error
    assert _REFRESH_TOKEN_REJECTED_MESSAGE not in error.message

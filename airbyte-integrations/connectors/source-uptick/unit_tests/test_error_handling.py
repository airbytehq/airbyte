# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the 401/403 response filters shared by every stream via
`definitions.linked.HttpRequester.error_handler` in `manifest.yaml`.

Both statuses must fail immediately as `config_error` with the connector's own message instead of
retrying or surfacing a raw HTTP error. `task_profitability` is used because it has no record
transformations, and it is the endpoint that returns 403 in production for users without the
Intelligence-report permission.
"""

import pytest
from conftest import base_config, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_STREAM_NAME = "task_profitability"
_BASE_URL = "https://demo.onuptick.com"
_TOKEN_REQUEST_BODY = "grant_type=password&client_id=client-id&client_secret=client-secret&username=user%40example.com&password=password"


def _read_stream(status_code: int, response_body: str) -> tuple[int, list]:
    config = base_config()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(f"{_BASE_URL}/api/oauth2/token/", body=_TOKEN_REQUEST_BODY),
            HttpResponse('{"access_token": "token", "expires_in": 3600}', 200),
        )
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/api/v2/intelligencereports/profitability_by_task/", query_params=ANY_QUERY_PARAMS),
            HttpResponse(response_body, status_code),
        )
        output = read(get_source(config, catalog), config, catalog)
    return len(output.records), output.errors


@pytest.mark.parametrize(
    "status_code, expected_message",
    [
        pytest.param(401, "HTTP 401: Uptick rejected the client credentials or user login.", id="401_config_error"),
        pytest.param(403, "HTTP 403: Uptick user lacks permission for the requested endpoint.", id="403_config_error"),
    ],
)
def test_auth_failures_fail_fast_as_config_error(status_code: int, expected_message: str) -> None:
    record_count, errors = _read_stream(status_code, '{"detail": "denied"}')

    assert record_count == 0
    stream_errors = [error.trace.error for error in errors if error.trace.error.message == expected_message]
    assert len(stream_errors) == 1, f"expected exactly one stream error with the connector message, got {errors}"
    assert stream_errors[0].failure_type == FailureType.config_error


def test_successful_read_emits_records() -> None:
    record_count, errors = _read_stream(
        200, '{"results": [{"task_id": 1, "updated": "2024-01-01T00:00:00.000000+0000"}], "links": {"next": null}}'
    )

    assert errors == []
    assert record_count == 1

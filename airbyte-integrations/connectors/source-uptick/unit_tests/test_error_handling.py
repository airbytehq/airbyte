# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the 403 response filter shared by every stream via
`definitions.linked.HttpRequester.error_handler` in `manifest.yaml`.

403 responses fail immediately as `config_error` with the connector's own message and without
retrying. 401 behaviour is split: bad credentials fail on the token endpoint as `config_error`,
while a 401 on a stream request refreshes the token and retries — both cases are covered in
`mock_server/test_error_handling.py`.
`task_profitability` is used because it has no record transformations, and it is the endpoint that returns 403 in production for users
without the Intelligence-report permission.
"""

from unittest.mock import patch

from conftest import base_config, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_STREAM_NAME = "task_profitability"
_BASE_URL = "https://demo.onuptick.com"
_TOKEN_REQUEST_BODY = "grant_type=password&client_id=client-id&client_secret=client-secret&username=user%40example.com&password=password"


def _read_stream(status_code: int, response_body: str) -> tuple[int, list, list[float], HttpMocker, HttpRequest, HttpRequest]:
    sleeps: list[float] = []
    with patch("time.sleep", sleeps.append):
        config = base_config()
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        with HttpMocker() as http_mocker:
            token_request = HttpRequest(f"{_BASE_URL}/api/oauth2/token/", body=_TOKEN_REQUEST_BODY)
            stream_request = HttpRequest(f"{_BASE_URL}/api/v2/intelligencereports/profitability_by_task/", query_params=ANY_QUERY_PARAMS)
            http_mocker.post(token_request, HttpResponse('{"access_token": "token", "expires_in": 3600}', 200))
            http_mocker.get(stream_request, HttpResponse(response_body, status_code))
            output = read(get_source(config, catalog), config, catalog)
    return len(output.records), output.errors, sleeps, http_mocker, token_request, stream_request


def _assert_single_config_error(errors: list, message: str) -> None:
    stream_errors = [error.trace.error for error in errors if error.trace.error.message == message]
    assert len(stream_errors) == 1, f"expected exactly one stream error with the connector message, got {errors}"
    assert stream_errors[0].failure_type == FailureType.config_error


def test_403_fails_fast_as_config_error() -> None:
    record_count, errors, sleeps, http_mocker, token_request, stream_request = _read_stream(403, '{"detail": "denied"}')
    message = "HTTP 403: Uptick user lacks permission for the requested endpoint."

    assert record_count == 0
    _assert_single_config_error(errors, message)
    http_mocker.assert_number_of_calls(token_request, 1)
    http_mocker.assert_number_of_calls(stream_request, 1)
    assert sleeps == []


def test_successful_read_emits_records() -> None:
    record_count, errors, _, _, _, _ = _read_stream(
        200, '{"results": [{"task_id": 1, "updated": "2024-01-01T00:00:00.000000+0000"}], "links": {"next": null}}'
    )

    assert errors == []
    assert record_count == 1

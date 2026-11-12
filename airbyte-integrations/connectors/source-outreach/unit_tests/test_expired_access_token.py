# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import _YAML_FILE_PATH
from unit_tests.conftest import build_source as get_source


_BASE_URL = "https://api.outreach.io/api/v2"
_TOKEN_URL = "https://api.outreach.io/oauth/token"
_START_CURSOR = "2020-11-16T00:00:00.000Z"
_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
_STREAMS = yaml.safe_load(Path(_YAML_FILE_PATH).read_text())["definitions"]["streams"]
_EXPIRED_TOKEN_BODY = {
    "errors": [{"id": "expiredAccessToken", "title": "Expired Access Token", "detail": "Please get a new access token and try again."}]
}


def _token_request() -> HttpRequest:
    return HttpRequest(
        _TOKEN_URL,
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )


def _token_response(access_token: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _stream_request(stream_name: str, access_token: str) -> HttpRequest:
    stream = _STREAMS[stream_name]
    requester = stream["retriever"]["requester"]
    return HttpRequest(
        f"{_BASE_URL}{requester['path']}",
        query_params={**requester["request_parameters"], stream["incremental_sync"]["start_time_option"]["field_name"]: _START_CURSOR},
        headers={"Authorization": f"Bearer {access_token}"},
    )


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", ["mailings", "calls", "prospects"])
def test_expired_access_token_is_refreshed_and_request_retried(stream_name: str) -> None:
    record = {"id": 1, "type": stream_name, "attributes": {"updatedAt": "2021-01-01T00:00:00.000Z"}}
    token_request = _token_request()
    expired_request = _stream_request(stream_name, "expired-token")
    fresh_request = _stream_request(stream_name, "fresh-token")
    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("expired-token"), _token_response("fresh-token")])
        http_mocker.get(
            expired_request,
            HttpResponse(body=json.dumps(_EXPIRED_TOKEN_BODY), status_code=401),
        )
        http_mocker.get(
            fresh_request,
            HttpResponse(body=json.dumps({"data": [record]}), status_code=200),
        )

        output = _read(stream_name)

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)

    assert not output.errors
    assert [r.record.data for r in output.records] == [{"updatedAt": "2021-01-01T00:00:00.000Z", "id": 1}]


def test_401_after_token_refresh_fails_as_config_error_without_refresh_loop() -> None:
    token_request = _token_request()
    first_request = _stream_request("mailings", "token-1")
    second_request = _stream_request("mailings", "token-2")
    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("token-1"), _token_response("token-2")])
        http_mocker.get(
            first_request,
            HttpResponse(body=json.dumps(_EXPIRED_TOKEN_BODY), status_code=401),
        )
        http_mocker.get(
            second_request,
            HttpResponse(body=json.dumps(_EXPIRED_TOKEN_BODY), status_code=401),
        )

        output = _read("mailings")

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    assert output.records == []
    stream_errors = [e.trace.error for e in output.errors if e.trace.error.stream_descriptor is not None]
    assert [(e.failure_type, e.message) for e in stream_errors] == [
        (FailureType.config_error, "Refreshed OAuth access token is rejected by the API.")
    ]

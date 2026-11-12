# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source as get_source
from unit_tests.test_jsonapi_records import _CONFIG, _TOKEN_URL, _query_params, _request, _resource, _response


_TOKEN_REQUEST_BODY = "grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token"
_EXPIRED_TOKEN_RESPONSE = HttpResponse(
    body=json.dumps(
        {
            "errors": [
                {
                    "id": "expiredAccessToken",
                    "title": "Expired Access Token",
                    "detail": "Please get a new access token and try again.",
                }
            ]
        }
    ),
    status_code=401,
)


def _token_response(access_token: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _authorized_request(stream_name: str, access_token: str) -> HttpRequest:
    request = _request(stream_name)
    return HttpRequest(
        request._parsed_url._replace(query="").geturl(),
        query_params=_query_params(stream_name),
        headers={"Authorization": f"Bearer {access_token}"},
    )


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    with patch("time.sleep", return_value=None):
        return read(get_source(config=_CONFIG, state=state), _CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", ["calls", "mailings"])
def test_expired_access_token_mid_sync_is_refreshed_and_request_retried(stream_name: str) -> None:
    resource = _resource("record-1", {"updatedAt": "2021-01-01T00:00:00.000Z"})

    token_request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
    stale_request = _authorized_request(stream_name, "stale-access-token")
    fresh_request = _authorized_request(stream_name, "fresh-access-token")

    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("stale-access-token"), _token_response("fresh-access-token")])
        http_mocker.get(stale_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _response([resource]))

        output = _read_stream(stream_name)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["record-1"]
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(stale_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)


def test_access_token_rejected_again_after_refresh_fails_without_refresh_loop() -> None:
    token_request = HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
    stale_request = _authorized_request("calls", "stale-access-token")
    fresh_request = _authorized_request("calls", "fresh-access-token")

    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, [_token_response("stale-access-token"), _token_response("fresh-access-token")])
        http_mocker.get(stale_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _EXPIRED_TOKEN_RESPONSE)

        output = _read_stream("calls")

        assert output.records == []
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message == "Refreshed OAuth access token is rejected by the API."
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(stale_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)

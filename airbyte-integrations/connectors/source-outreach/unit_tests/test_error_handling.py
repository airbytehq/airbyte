# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source
from unit_tests.test_jsonapi_records import _BASE_URL, _CONFIG, _STREAMS, _TOKEN_URL, _query_params, _resource, _response


_EXPIRED_TOKEN = "expired-access-token"
_FRESH_TOKEN = "fresh-access-token"
_EXPIRED_TOKEN_RESPONSE = HttpResponse(
    body=json.dumps(
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        }
    ),
    status_code=401,
)


def _token_response(access_token: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": access_token, "expires_in": 7200}), status_code=200)


def _mock_token_refreshes(http_mocker: HttpMocker) -> HttpRequest:
    """The token endpoint hands out the soon-to-expire token first and a fresh one on every later refresh."""
    token_request = HttpRequest(
        _TOKEN_URL,
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )
    http_mocker.post(token_request, [_token_response(_EXPIRED_TOKEN), _token_response(_FRESH_TOKEN)])
    return token_request


def _authenticated_request(stream_name: str, access_token: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}{_STREAMS[stream_name]['retriever']['requester']['path']}",
        query_params=_query_params(stream_name),
        headers={"Authorization": f"Bearer {access_token}"},
    )


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(build_source(config=_CONFIG, state=state), _CONFIG, catalog, state, expecting_exception=True)


@pytest.fixture(autouse=True)
def no_backoff_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _seconds: None)


@pytest.mark.parametrize("stream_name", ["mailings", "calls"])
def test_expired_access_token_is_refreshed_and_request_retried(stream_name: str) -> None:
    resource = _resource("1", {"updatedAt": "2021-01-01T00:00:00.000Z"})

    with HttpMocker() as http_mocker:
        token_request = _mock_token_refreshes(http_mocker)
        expired_request = _authenticated_request(stream_name, _EXPIRED_TOKEN)
        fresh_request = _authenticated_request(stream_name, _FRESH_TOKEN)
        http_mocker.get(expired_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _response([resource]))

        output = _read_stream(stream_name)

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)

    assert not output.errors
    assert [record.record.data for record in output.records] == [{"updatedAt": "2021-01-01T00:00:00.000Z", "id": "1"}]


def test_401_after_token_refresh_fails_as_config_error_without_refreshing_again() -> None:
    with HttpMocker() as http_mocker:
        token_request = _mock_token_refreshes(http_mocker)
        expired_request = _authenticated_request("mailings", _EXPIRED_TOKEN)
        fresh_request = _authenticated_request("mailings", _FRESH_TOKEN)
        http_mocker.get(expired_request, _EXPIRED_TOKEN_RESPONSE)
        http_mocker.get(fresh_request, _EXPIRED_TOKEN_RESPONSE)

        output = _read_stream("mailings")

        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(fresh_request, 1)

    assert output.records == []
    # The CDK emits the stream-level failure first, followed by the end-of-sync summary error.
    stream_error = output.errors[0].trace.error
    assert stream_error.failure_type == FailureType.config_error
    assert stream_error.message == "Refreshed OAuth access token is rejected by the API."
    assert stream_error.stream_descriptor.name == "mailings"

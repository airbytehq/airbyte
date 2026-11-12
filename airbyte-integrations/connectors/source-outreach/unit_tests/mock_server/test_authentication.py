# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source
from unit_tests.mock_server.request_builder import TOKEN_REQUEST, page_request, page_url


CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
EXPIRED_TOKEN = HttpResponse(
    body=json.dumps(
        {
            "id": "expiredAccessToken",
            "title": "Expired Access Token",
            "detail": "Please get a new access token and try again.",
        }
    ),
    status_code=401,
)


def token_response(token: str) -> HttpResponse:
    # The server can reject a token before the client's locally calculated expiry.
    return HttpResponse(body=json.dumps({"access_token": token, "expires_in": 7200}), status_code=200)


def record_response(record_id: int, next_url: str | None = None) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "data": [{"id": record_id, "attributes": {"updatedAt": f"2021-01-0{record_id}T00:00:00.000Z"}}],
                "links": {"next": next_url},
            }
        ),
        status_code=200,
    )


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().build()
    return read(build_source(config=CONFIG, state=state), CONFIG, catalog, state)


@pytest.mark.parametrize("stream_name", ["calls", "mailings"])
def test_read_refreshes_server_expired_token_and_resumes_same_page(stream_name: str) -> None:
    first_page = page_request(stream_name, "old-token")
    expired_page = page_request(stream_name, "old-token", after="next-page")
    retried_page = page_request(stream_name, "new-token", after="next-page")

    with HttpMocker() as http_mocker:
        http_mocker.post(TOKEN_REQUEST, [token_response("old-token"), token_response("new-token")])
        http_mocker.get(first_page, record_response(1, page_url(stream_name, after="next-page")))
        http_mocker.get(expired_page, EXPIRED_TOKEN)
        http_mocker.get(retried_page, record_response(2))

        output = read_stream(stream_name)

        assert not output.errors, output.get_formatted_error_message()
        assert [record.record.data for record in output.records] == [
            {"id": 1, "updatedAt": "2021-01-01T00:00:00.000Z"},
            {"id": 2, "updatedAt": "2021-01-02T00:00:00.000Z"},
        ]
        assert output.state_messages[-1].state.stream.stream_state.updatedAt == "2021-01-02T00:00:00.000Z"
        http_mocker.assert_number_of_calls(TOKEN_REQUEST, 2)
        for request in (first_page, expired_page, retried_page):
            http_mocker.assert_number_of_calls(request, 1)


def test_rejected_refreshed_token_fails_without_refresh_loop() -> None:
    expired_page = page_request("mailings", "old-token")
    rejected_page = page_request("mailings", "new-token")

    with HttpMocker() as http_mocker:
        http_mocker.post(TOKEN_REQUEST, [token_response("old-token"), token_response("new-token")])
        http_mocker.get(expired_page, EXPIRED_TOKEN)
        http_mocker.get(rejected_page, EXPIRED_TOKEN)

        output = read_stream("mailings")

        assert output.records == []
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message == "Refreshed OAuth access token is rejected by the API."
        http_mocker.assert_number_of_calls(TOKEN_REQUEST, 2)
        http_mocker.assert_number_of_calls(expired_page, 1)
        http_mocker.assert_number_of_calls(rejected_page, 1)


@pytest.mark.parametrize("status_code, error_id", [(401, "invalidAccessToken"), (403, "forbidden")])
def test_other_auth_errors_fail_without_refresh(status_code: int, error_id: str) -> None:
    request = page_request("mailings", "old-token")

    with HttpMocker() as http_mocker:
        http_mocker.post(TOKEN_REQUEST, token_response("old-token"))
        http_mocker.get(request, HttpResponse(body=json.dumps({"id": error_id}), status_code=status_code))

        output = read_stream("mailings")

        assert output.records == []
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        expected = (
            "HTTP Status Code: 401. Error: Unauthorized. Please ensure you are authenticated correctly."
            if status_code == 401
            else "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
        )
        assert error.message == expected
        http_mocker.assert_number_of_calls(TOKEN_REQUEST, 1)
        http_mocker.assert_number_of_calls(request, 1)

# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


TOKEN_URL = "https://api.outreach.io/oauth/token"
MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"
NEXT_URL = MAILINGS_URL + "?page[after]=1"
EXPIRED_TOKEN = {
    "id": "expiredAccessToken",
    "title": "Expired Access Token",
    "detail": "Please get a new access token and try again.",
}


@pytest.fixture
def config():
    return {
        "client_id": "test-client",
        "client_secret": "test-secret",
        "refresh_token": "test-refresh",
        "redirect_uri": "https://example.com/callback",
        "start_date": "2024-01-01T00:00:00Z",
    }


def response(body, status=200):
    return HttpResponse(body=json.dumps(body), status_code=status)


def page(ids, next_url=None):
    return response(
        {
            "data": [{"id": record_id, "attributes": {"updatedAt": "2024-01-02T00:00:00.000Z"}} for record_id in ids],
            "links": {"next": next_url},
        }
    )


def request(token, next_page=False):
    params = {"count": "false", "sort": "updatedAt", "page[size]": "100", "newFilterSyntax": "true"}
    params["filter[updatedAt][gte]"] = "2024-01-01T00:00:00.000Z"
    if next_page:
        params["page[after]"] = "1"
    return HttpRequest(MAILINGS_URL, query_params=params, headers={"Authorization": f"Bearer {token}"})


def read_mailings(source, config):
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    return read(source, config=config, catalog=catalog)


@pytest.mark.parametrize("second_page_ids", [[2, 3], []], ids=["records", "empty"])
def test_refreshes_expired_token_mid_pagination(source, config, second_page_ids):
    with HttpMocker() as http_mocker:
        token_request = HttpRequest(
            TOKEN_URL, body="grant_type=refresh_token&client_id=test-client&client_secret=test-secret&refresh_token=test-refresh"
        )
        http_mocker.post(token_request, [response({"access_token": token, "expires_in": 3600}) for token in ["token-A", "token-B"]])
        http_mocker.get(request("token-A"), page([1], NEXT_URL))
        http_mocker.get(request("token-A", next_page=True), response(EXPIRED_TOKEN, 401))
        retried_request = request("token-B", next_page=True)
        http_mocker.get(retried_request, page(second_page_ids))

        output = read_mailings(source, config)

        assert [message.record.data["id"] for message in output.records] == [1, *second_page_ids]
        assert output.errors == []
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(retried_request, 1)
        assert output.get_stream_statuses("mailings")[-1] == AirbyteStreamStatus.COMPLETE


def test_persistent_unauthorized_fails_after_refresh(source, config):
    with HttpMocker() as http_mocker:
        token_request = HttpRequest(
            TOKEN_URL, body="grant_type=refresh_token&client_id=test-client&client_secret=test-secret&refresh_token=test-refresh"
        )
        http_mocker.post(token_request, [response({"access_token": token, "expires_in": 3600}) for token in ["token-A", "token-B"]])
        http_mocker.get(request("token-A"), page([1], NEXT_URL))
        expired_request = request("token-A", next_page=True)
        retried_request = request("token-B", next_page=True)
        http_mocker.get(expired_request, response(EXPIRED_TOKEN, 401))
        http_mocker.get(retried_request, response(EXPIRED_TOKEN, 401))

        output = read_mailings(source, config)

        assert [message.record.data["id"] for message in output.records] == [1]
        assert output.errors
        assert all(message.trace.error.failure_type == FailureType.config_error for message in output.errors)
        assert output.get_stream_statuses("mailings")[-1] == AirbyteStreamStatus.INCOMPLETE
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(retried_request, 1)


@pytest.mark.parametrize("status", [429, 500, 503])
def test_unmatched_status_uses_default_retry(source, config, status):
    with HttpMocker() as http_mocker:
        token_request = HttpRequest(
            TOKEN_URL, body="grant_type=refresh_token&client_id=test-client&client_secret=test-secret&refresh_token=test-refresh"
        )
        http_mocker.post(token_request, response({"access_token": "token-A", "expires_in": 3600}))
        page_request = request("token-A")
        http_mocker.get(page_request, [response({}, status), page([1])])

        output = read_mailings(source, config)

        assert [message.record.data["id"] for message in output.records] == [1]
        assert output.errors == []
        http_mocker.assert_number_of_calls(token_request, 1)
        http_mocker.assert_number_of_calls(page_request, 2)

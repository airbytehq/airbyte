# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import build_source


_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
_EXPIRED_TOKEN = HttpResponse(
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


@pytest.mark.parametrize("after_refresh", ["record", "empty", "unauthorized"])
def test_refresh_expired_access_token(after_refresh: str) -> None:
    token_request = HttpRequest(
        "https://api.outreach.io/oauth/token",
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )
    requests = [
        HttpRequest(
            "https://api.outreach.io/api/v2/accounts",
            query_params={
                "count": "false",
                "sort": "updatedAt",
                "page[size]": "1000",
                "newFilterSyntax": "true",
                "filter[updatedAt][gte]": "2020-11-16T00:00:00.000Z",
            },
            headers={"Authorization": f"Bearer token-{number}"},
        )
        for number in (1, 2)
    ]
    records = [{"id": "account-1", "attributes": {"updatedAt": "2021-01-01T00:00:00.000Z"}}] if after_refresh == "record" else []
    response = _EXPIRED_TOKEN if after_refresh == "unauthorized" else HttpResponse(body=json.dumps({"data": records}), status_code=200)
    catalog = CatalogBuilder().with_stream("accounts", SyncMode.incremental).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            [HttpResponse(body=json.dumps({"access_token": f"token-{number}", "expires_in": 7200}), status_code=200) for number in (1, 2)],
        )
        http_mocker.get(requests[0], _EXPIRED_TOKEN)
        http_mocker.get(requests[1], response)
        output = read(build_source(_CONFIG), _CONFIG, catalog)

        if after_refresh == "unauthorized":
            assert not output.records
            assert output.errors
            assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        else:
            assert not output.errors
            assert [record.record.data["id"] for record in output.records] == (["account-1"] if records else [])
        http_mocker.assert_number_of_calls(token_request, 2)
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

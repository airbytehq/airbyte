# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


def test_mailings_refreshes_expired_access_token() -> None:
    config = {
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token",
        "redirect_uri": "https://example.com",
        "start_date": "2026-01-01T00:00:00Z",
    }
    token_request = HttpRequest(
        "https://api.outreach.io/oauth/token",
        body="grant_type=refresh_token&client_id=client-id&client_secret=client-secret&refresh_token=refresh-token",
    )
    expired_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings", query_params=ANY_QUERY_PARAMS, headers={"Authorization": "Bearer A"}
    )
    retried_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings", query_params=ANY_QUERY_PARAMS, headers={"Authorization": "Bearer B"}
    )
    record = {"id": 123, "updatedAt": "2026-01-02T00:00:00.000Z"}
    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            [HttpResponse(body=json.dumps({"access_token": token, "expires_in": 7200})) for token in ("A", "B")],
        )
        http_mocker.get(
            expired_request,
            HttpResponse(body=json.dumps({"errors": [{"id": "expiredAccessToken", "title": "Expired Access Token"}]}), status_code=401),
        )
        http_mocker.get(
            retried_request,
            HttpResponse(body=json.dumps({"data": [{"id": record["id"], "attributes": {"updatedAt": record["updatedAt"]}}]})),
        )

        output = read(get_source(config), config, CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build())

        assert [message.record.data for message in output.records] == [record]
        assert not output.errors
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(retried_request, 1)

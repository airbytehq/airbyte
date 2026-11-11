# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


def test_mailings_refreshes_expired_access_token(source, config):
    token_request = HttpRequest(
        "https://api.outreach.io/oauth/token",
        body="grant_type=refresh_token&client_id=client&client_secret=secret&refresh_token=refresh",
    )
    first_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings",
        query_params=ANY_QUERY_PARAMS,
        headers={"Authorization": "Bearer A"},
    )
    retry_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings",
        query_params=ANY_QUERY_PARAMS,
        headers={"Authorization": "Bearer B"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            [HttpResponse(json.dumps({"access_token": token, "expires_in": 7200})) for token in ("A", "B")],
        )
        http_mocker.get(
            first_request,
            HttpResponse(
                json.dumps(
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
            ),
        )
        http_mocker.get(
            retry_request,
            HttpResponse(
                json.dumps(
                    {
                        "data": [{"id": 123, "attributes": {"updatedAt": "2024-01-02T00:00:00.000Z"}}],
                        "links": {"next": None},
                    }
                )
            ),
        )
        catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
        output = read(source, config, catalog, expecting_exception=True)

        assert not output.errors, output.errors
        assert [record.record.data["id"] for record in output.records] == [123]
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(retry_request, 1)

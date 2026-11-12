# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source


@pytest.mark.parametrize("data", [[{"id": 123, "attributes": {"updatedAt": "2021-01-01T00:00:00.000Z"}}], []])
def test_read_refreshes_expired_access_token(data: list[dict]) -> None:
    config = {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
        "redirect_uri": "https://example.com/callback",
        "start_date": "2020-11-16T00:00:00Z",
    }
    token_request = HttpRequest(
        "https://api.outreach.io/oauth/token",
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )
    query_params = {
        "page[size]": "100",
        "count": "false",
        "newFilterSyntax": "true",
        "sort": "updatedAt",
        "filter[updatedAt][gte]": "2020-11-16T00:00:00.000Z",
    }
    expired_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings", query_params=query_params, headers={"Authorization": "Bearer A"}
    )
    refreshed_request = HttpRequest(
        "https://api.outreach.io/api/v2/mailings", query_params=query_params, headers={"Authorization": "Bearer B"}
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            [
                HttpResponse(body='{"access_token":"A","expires_in":7200}', status_code=200),
                HttpResponse(body='{"access_token":"B","expires_in":7200}', status_code=200),
            ],
        )
        http_mocker.get(
            expired_request,
            HttpResponse(body='{"errors":[{"id":"expiredAccessToken","detail":"Access token expired"}]}', status_code=401),
        )
        http_mocker.get(refreshed_request, HttpResponse(body=json.dumps({"data": data}), status_code=200))
        state = StateBuilder().build()
        catalog = CatalogBuilder().with_stream("mailings", SyncMode.incremental).build()

        output = read(build_source(config, state), config, catalog, state)

        assert not output.errors
        assert [record.record.data for record in output.records] == [{"id": resource["id"], **resource["attributes"]} for resource in data]
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(expired_request, 1)
        http_mocker.assert_number_of_calls(refreshed_request, 1)

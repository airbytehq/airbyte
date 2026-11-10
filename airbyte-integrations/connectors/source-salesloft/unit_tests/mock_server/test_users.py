# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import SalesloftRequestBuilder
from mock_server.response_builder import SalesloftResponseBuilder


def _read_users(http_mocker: HttpMocker, config: dict, token: str) -> EntrypointOutput:
    requests = []
    for page, record_id, next_page in [(None, 101, 2), (2, 102, None)]:
        request_builder = SalesloftRequestBuilder.users(token)
        if page:
            request_builder.with_page(page)
        request = request_builder.build()
        requests.append(request)
        response = SalesloftResponseBuilder().with_records([{"id": record_id}])
        if next_page:
            response.with_next_page(next_page)
        http_mocker.get(request, response.build())
    output = read(get_source(config), config, CatalogBuilder().with_stream("users", SyncMode.full_refresh).build())
    assert [record.record.data["id"] for record in output.records] == [101, 102]
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)
    return output


def test_expired_oauth_token_is_refreshed_and_persisted() -> None:
    config = ConfigBuilder().build()
    token_request = HttpRequest(
        url="https://accounts.salesloft.com/oauth/token",
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=old-refresh-token",
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            HttpResponse(body=json.dumps({"access_token": "new-access-token", "refresh_token": "new-refresh-token", "expires_in": 3600})),
        )
        stdout = StringIO()
        with redirect_stdout(stdout):
            _read_users(http_mocker, config, "new-access-token")
        http_mocker.assert_number_of_calls(token_request, 1)
    controls = [json.loads(line) for line in stdout.getvalue().splitlines() if '"type":"CONTROL"' in line]
    assert len(controls) == 1
    assert controls[0]["control"]["type"] == "CONNECTOR_CONFIG"
    credentials = controls[0]["control"]["connectorConfig"]["config"]["credentials"]
    assert credentials["access_token"] == "new-access-token"
    assert credentials["refresh_token"] == "new-refresh-token"
    assert credentials["token_expiry_date"] != "2000-01-01T00:00:00Z"


@pytest.mark.parametrize("auth_type", ["oauth2.0", "api_key"])
def test_valid_credentials_do_not_refresh(auth_type: str) -> None:
    builder = ConfigBuilder().with_expiry("2099-01-01T00:00:00Z")
    token = "old-access-token"
    if auth_type == "api_key":
        builder.with_api_key("test-api-key")
        token = "test-api-key"
    with HttpMocker() as http_mocker:
        _read_users(http_mocker, builder.build(), token)
        assert len(http_mocker._mocker.request_history) == 2

#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs

import requests_mock
from source_genesys.source import SourceGenesys

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_read_authenticates_and_follows_pagination():
    config = {
        "tenant_endpoint": "Americas (US East)",
        "client_id": "cid",
        "client_secret": "csecret",
        "start_date": "2024-01-01",
    }
    token_url = "https://login.mypurecloud.com/oauth/token"
    users_url = "https://api.mypurecloud.com/api/v2/users"
    catalog = CatalogBuilder().with_stream("user_users", SyncMode.full_refresh).build()

    with requests_mock.Mocker() as http_mock:
        http_mock.post(token_url, json={"access_token": "tok", "expires_in": 3600})
        http_mock.get(
            f"{users_url}?pageSize=500",
            complete_qs=True,
            json={"entities": [{"id": "1"}], "nextUri": "/api/v2/users?pageSize=500&pageNumber=2"},
        )
        http_mock.get(
            f"{users_url}?pageSize=500&pageNumber=2",
            complete_qs=True,
            json={"entities": [{"id": "2"}]},
        )

        output = read(SourceGenesys(), config, catalog)

        assert [record.record.data["id"] for record in output.records] == ["1", "2"]
        assert not output.errors

        token_request = next(request for request in http_mock.request_history if request.method == "POST")
        body = parse_qs(token_request.text)
        assert body["grant_type"] == ["client_credentials"]
        assert body["client_id"] == ["cid"]
        assert body["client_secret"] == ["csecret"]

        get_requests = [request for request in http_mock.request_history if request.method == "GET"]
        assert len(get_requests) == 2
        assert all(request.headers["Authorization"] == "Bearer tok" for request in get_requests)

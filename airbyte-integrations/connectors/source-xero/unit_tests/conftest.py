#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    return {
        "authentication": {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
            "access_token": "access_token",
            "token_expiry_date": "2099-01-01T12:00:00.000000+00:00"
        },
        "tenant_id": "tenant_id",
        "start_date": "2020-01-01T00:00:00Z",
    }


@fixture(name="mock_response")
def mock_response():
    return {
        "data": [{"gid": "gid", "resource_type": "resource_type", "name": "name"}],
        "next_page": {"offset": "offset", "path": "path", "uri": "uri"},
    }


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None):
        if response is None:
            response = {}

        url = f"https://api.xero.com/api.xro/2.0/{path}"
        requests_mock.get(url, json=response)
        requests_mock.get("https://identity.xero.com/connect/token", json={})

    return _mock_stream


@fixture(name="mock_auth")
def mock_auth_fixture(requests_mock):
    def _mock_auth(response=None):
        if response is None:
            response = {}
        requests_mock.post("https://identity.xero.com/connect/token", json=response)

    return _mock_auth

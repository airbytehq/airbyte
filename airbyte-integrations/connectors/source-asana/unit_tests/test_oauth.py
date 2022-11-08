#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests_mock
from source_asana.oauth import AsanaOauth2Authenticator


@pytest.fixture
def req_mock():
    with requests_mock.Mocker() as mock:
        yield mock


def test_oauth(req_mock):
    URL = "https://example.com"
    TOKEN = "test_token"
    req_mock.post(URL, json={"access_token": TOKEN, "expires_in": 3600})
    a = AsanaOauth2Authenticator(
        token_refresh_endpoint=URL,
        client_secret="client_secret",
        client_id="client_id",
        refresh_token="refresh_token",
    )
    token = a.get_access_token()
    assert token == TOKEN
    assert "multipart/form-data;" in req_mock.last_request.headers["Content-Type"]
    assert "client_secret" in req_mock.last_request.body.decode()
    assert "client_id" in req_mock.last_request.body.decode()
    assert "refresh_token" in req_mock.last_request.body.decode()

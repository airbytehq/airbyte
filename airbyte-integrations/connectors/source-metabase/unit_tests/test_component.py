#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from requests.exceptions import HTTPError
from source_metabase.components import MetabaseAuth

config = {
    "instance_api_url": "https://airbyte.metabaseapp.com/api/",
    "username": "username",
    "password": "password",
    "session_token": "some token",
}


def test_get_auth_header():
    auth_header = MetabaseAuth(config, {}).get_auth_header()
    assert auth_header == {"X-Metabase-Session": "some token"}


def test_has_valid_token(requests_mock):
    requests_mock.get(f"{config['instance_api_url']}user/current", json={"common_name": "common_name", "last_login": "last_login"})

    assert MetabaseAuth(config, {}).has_valid_token()


def test_has_valid_token_unauthorized():
    with pytest.raises(HTTPError):
        MetabaseAuth(config, {}).has_valid_token()


def test_get_new_session_token_unauthorized():
    with pytest.raises(HTTPError):
        MetabaseAuth(config, {}).get_new_session_token(config["username"], config["password"])


def test_get_new_session_token(requests_mock):
    requests_mock.post(f"{config['instance_api_url']}session", headers={"Content-Type": "application/json"}, json={"id": "some session id"})

    session_token = MetabaseAuth(config, {}).get_new_session_token(config["username"], config["password"])
    assert session_token == "some session id"

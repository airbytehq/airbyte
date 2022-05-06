#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(autouse=True)
def mock_oauth_call(requests_mock):
    yield requests_mock.post(
        "https://accounts.google.com/o/oauth2/token",
        json={"access_token": "access_token", "refresh_token": "refresh_token", "expires_in": 0},
    )

#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(scope="session", name="oauth_config")
def oauth_config_fixture():
    with open("secrets/config_oauth.json", "r") as config_file:
        return json.load(config_file)

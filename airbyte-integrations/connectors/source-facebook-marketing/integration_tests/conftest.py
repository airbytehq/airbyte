#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json

import pytest


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(scope="session", name="config_with_wrong_token")
def config_with_wrong_token_fixture(config):
    return {**config, "access_token": "WRONG_TOKEN"}


@pytest.fixture(scope="session", name="config_with_wrong_account")
def config_with_wrong_account_fixture(config):
    return {**config, "account_id": "WRONG_ACCOUNT"}


@pytest.fixture(scope="session", name="config_with_include_deleted")
def config_with_include_deleted_fixture(config):
    new_config = {**config, "include_deleted": True}
    new_config.pop("_limit", None)
    new_config.pop("end_date", None)
    return new_config

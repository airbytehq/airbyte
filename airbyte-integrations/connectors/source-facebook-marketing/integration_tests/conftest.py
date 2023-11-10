#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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


@pytest.fixture(scope="session", name="config_with_statuses_fixture")
def config_with_statuses_fixture(config):
    new_config = {
        **config,
        "campaign_statuses": ["ACTIVE"],
        "adset_statuses": ["ACTIVE"],
        "ad_statuses": ["ACTIVE"],
        "adcreative_statuses": ["ACTIVE"],
    }
    new_config.pop("_limit", None)
    new_config.pop("end_date", None)
    return new_config

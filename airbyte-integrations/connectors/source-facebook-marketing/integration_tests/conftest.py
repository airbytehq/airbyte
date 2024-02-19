#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

import pytest
from source_facebook_marketing.config_migrations import MigrateAccountIdToArray


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        config = json.load(config_file)
        migrated_config = MigrateAccountIdToArray.transform(config)
        return migrated_config


@pytest.fixture(scope="session", name="config_with_wrong_token")
def config_with_wrong_token_fixture(config):
    return {**config, "access_token": "WRONG_TOKEN"}


@pytest.fixture(scope="session", name="config_with_wrong_account")
def config_with_wrong_account_fixture(config):
    return {**config, "account_ids": ["WRONG_ACCOUNT"]}


@pytest.fixture(scope="session", name="config_with_include_deleted")
def config_with_include_deleted(config):
    new_config = {
        **config,
        "campaign_statuses": [
            "ACTIVE",
            "ARCHIVED",
            "DELETED",
            "IN_PROCESS",
            "PAUSED",
            "WITH_ISSUES",
        ],
        "adset_statuses": [
            "ACTIVE",
            "ARCHIVED",
            "CAMPAIGN_PAUSED",
            "DELETED",
            "IN_PROCESS",
            "PAUSED",
            "WITH_ISSUES",
        ],
        "ad_statuses": [
            "ACTIVE",
            "ADSET_PAUSED",
            "ARCHIVED",
            "CAMPAIGN_PAUSED",
            "DELETED",
            "DISAPPROVED",
            "IN_PROCESS",
            "PAUSED",
            "PENDING_BILLING_INFO",
            "PENDING_REVIEW",
            "PREAPPROVED",
            "WITH_ISSUES",
        ],
    }
    new_config.pop("_limit", None)
    new_config.pop("end_date", None)
    return new_config

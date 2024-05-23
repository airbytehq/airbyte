#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from source_mailchimp import SourceMailchimp
from source_mailchimp.config_migrations import MigrateDataCenter

# BASE ARGS
SOURCE: YamlDeclarativeSource = SourceMailchimp()


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


@pytest.mark.parametrize(
    "config_path",
    [
        (f"{os.path.dirname(__file__)}/test_configs/test_config_api_key.json"),
        (f"{os.path.dirname(__file__)}/test_configs/test_config_oauth.json"),
    ],
    ids=["test_requester_datacenter_with_api_key", "test_requester_datacenter_with_oauth_flow"],
)
def test_mailchimp_config_migration(config_path: str, requests_mock):
    requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"dc": "us10"})

    migration_instance = MigrateDataCenter
    migration_instance.migrate(["check", "--config", config_path], SOURCE)
    test_migrated_config = load_config(config_path)
    assert test_migrated_config.get("data_center") == "us10"

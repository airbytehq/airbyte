#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
from typing import Any, Mapping

import pytest
from unit_tests.conftest import get_source
# from source_declarative_manifest.components import MigrateDataCenter


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)

# TODO Enable this unit test once the config migration logic is added to the PR
# @pytest.mark.parametrize(
#     "config_path",
#     [
#         (f"{os.path.dirname(__file__)}/test_configs/test_config_api_key.json"),
#         (f"{os.path.dirname(__file__)}/test_configs/test_config_oauth.json"),
#     ],
#     ids=["test_requester_datacenter_with_api_key", "test_requester_datacenter_with_oauth_flow"],
# )
# def test_mailchimp_config_migration(config_path: str, requests_mock):
#     requests_mock.get("https://login.mailchimp.com/oauth2/metadata", json={"dc": "us10"})
#
#     try:
#         config: Mapping[str, Any] = load_config(config_path)
#         source = get_source(config)
#         migration_instance = MigrateDataCenter
#         migration_instance.migrate(["check", "--config", config_path], source)
#         test_migrated_config = load_config(config_path)
#         assert test_migrated_config.get("data_center") == "us10"
#     finally:
#         with open(config_path, "w") as f:
#             json.dump(config, f)

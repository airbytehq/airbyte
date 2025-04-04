# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os
from typing import Any, Mapping

from source_slack import SourceSlack
from source_slack.config_migrations import MigrateLegacyConfig


CMD = "check"
TEST_CONFIG_LEGACY_PATH = f"{os.path.dirname(__file__)}/configs/legacy_config.json"
TEST_CONFIG_ACTUAL_PATH = f"{os.path.dirname(__file__)}/configs/actual_config.json"

SOURCE_INPUT_ARGS_LEGACY = [CMD, "--config", TEST_CONFIG_LEGACY_PATH]
SOURCE_INPUT_ARGS_ACTUAL = [CMD, "--config", TEST_CONFIG_ACTUAL_PATH]


def revert_config():
    with open(TEST_CONFIG_LEGACY_PATH, "r") as test_config:
        config = json.load(test_config)
        config.pop("credentials")
        config.update({"api_token": "api-token"})
        with open(TEST_CONFIG_LEGACY_PATH, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def load_config(config_path: str = TEST_CONFIG_LEGACY_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_config_migration():
    migration = MigrateLegacyConfig()
    migration.migrate(SOURCE_INPUT_ARGS_LEGACY, SourceSlack())
    test_migrated_config = load_config()
    assert test_migrated_config["credentials"]["api_token"] == "api-token"
    assert test_migrated_config["credentials"]["option_title"] == "API Token Credentials"
    revert_config()


def test_config_not_migrated():
    config_before_migration = load_config(TEST_CONFIG_ACTUAL_PATH)
    migration = MigrateLegacyConfig()
    migration.migrate(SOURCE_INPUT_ARGS_ACTUAL, SourceSlack())
    test_migrated_config = load_config(TEST_CONFIG_ACTUAL_PATH)
    assert config_before_migration == test_migrated_config

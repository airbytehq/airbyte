#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import Any, Mapping

import pytest
from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_harvest.config_migrations import MigrateAuthType
from source_harvest.source import SourceHarvest

# BASE ARGS
CMD = "check"
TEST_TOKEN_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"
NEW_TEST_TOKEN_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_new_config.json"
TEST_OAUTH_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config_oauth.json"
NEW_TEST_OAUTH_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_new_config_oauth.json"
SOURCE: Source = SourceHarvest()

# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config["credentials"].pop("auth_type")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


@pytest.mark.parametrize(
    "config_path, expected_auth_type",
    [
        (TEST_TOKEN_CONFIG_PATH, "Token"),
        (TEST_OAUTH_CONFIG_PATH, "Client"),
    ],
)
def test_migrate_config(config_path, expected_auth_type):

    source_input_args = [CMD, "--config", config_path]

    migration_instance = MigrateAuthType

    migration_instance.migrate(source_input_args, SOURCE)

    test_migrated_config = load_config(config_path)

    # Verify migrated property
    assert "auth_type" in test_migrated_config["credentials"]
    assert test_migrated_config["credentials"]["auth_type"] == expected_auth_type

    # Test CONTROL MESSAGE was emitted)
    control_message = migration_instance.message_repository._message_queue[0]
    assert control_message.type == Type.CONTROL
    assert control_message.control.type == OrchestratorType.CONNECTOR_CONFIG

    revert_migration(config_path)


@pytest.mark.parametrize(
    "config_path",
    [
        NEW_TEST_TOKEN_CONFIG_PATH,
        NEW_TEST_OAUTH_CONFIG_PATH,
    ],
)
def test_should_not_migrate_new(config_path):
    new_config = load_config(config_path)
    instance = MigrateAuthType
    assert not instance.should_migrate(new_config)



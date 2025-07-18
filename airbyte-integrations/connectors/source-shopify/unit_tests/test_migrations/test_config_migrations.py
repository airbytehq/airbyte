#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from source_shopify.config_migrations import MigrateConfig
from source_shopify.source import SourceShopify

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source


# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_config.json"
NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_new_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceShopify()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("start_date")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config() -> None:
    migration_instance = MigrateConfig()
    # original_config = load_config()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "start_date" in test_migrated_config
    # check the data type
    assert isinstance(test_migrated_config["start_date"], str)
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # check the migrated values
    assert control_msg.control.connectorConfig.config["start_date"] == "2020-01-01"
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "start_date" not in test_config


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    migration_instance = MigrateConfig()
    assert not migration_instance.should_migrate(new_config)

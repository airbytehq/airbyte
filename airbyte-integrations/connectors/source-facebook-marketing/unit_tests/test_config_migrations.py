#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_facebook_marketing.config_migrations import MigrateAccountIdToArray
from source_facebook_marketing.source import SourceFacebookMarketing

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_old_config.json"
NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_new_config.json"
UPGRADED_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_upgraded_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceFacebookMarketing()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("account_ids")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config():
    migration_instance = MigrateAccountIdToArray()
    original_config = load_config()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "account_ids" in test_migrated_config
    assert isinstance(test_migrated_config["account_ids"], list)
    # check the old property is in place
    assert "account_id" in test_migrated_config
    assert isinstance(test_migrated_config["account_id"], str)
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # load the old custom reports VS migrated
    assert [original_config["account_id"]] == test_migrated_config["account_ids"]
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # old custom_reports are stil type(str)
    assert isinstance(control_msg.control.connectorConfig.config["account_id"], str)
    # new custom_reports are type(list)
    assert isinstance(control_msg.control.connectorConfig.config["account_ids"], list)
    # check the migrated values
    assert control_msg.control.connectorConfig.config["account_ids"] == ["01234567890"]
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "account_ids" not in test_config
    # check the old property is still there
    assert "account_id" in test_config
    assert isinstance(test_config["account_id"], str)


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    migration_instance = MigrateAccountIdToArray()
    assert not migration_instance.should_migrate(new_config)

def test_should_not_migrate_upgraded_config():
    new_config = load_config(UPGRADED_TEST_CONFIG_PATH)
    migration_instance = MigrateAccountIdToArray()
    assert not migration_instance.should_migrate(new_config)

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_surveymonkey.config_migrations import MigrateAccessTokenToCredentials
from source_surveymonkey.source import SourceSurveymonkey

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_old_config.json"
NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_new_config.json"
UPGRADED_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_upgraded_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceSurveymonkey()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("credentials")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config():
    migration_instance = MigrateAccessTokenToCredentials()
    original_config = load_config()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "credentials" in test_migrated_config
    assert isinstance(test_migrated_config["credentials"], dict)
    assert "access_token" in test_migrated_config["credentials"]
    assert isinstance(test_migrated_config["access_token"], str)
    assert "auth_method" in test_migrated_config["credentials"]
    assert test_migrated_config["credentials"]["auth_method"] == "oauth2.0"
    # check the old property is in place
    assert "access_token" in test_migrated_config
    assert isinstance(test_migrated_config["access_token"], str)
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # load the old custom reports VS migrated
    assert original_config["access_token"] == test_migrated_config["credentials"]["access_token"]
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # old custom_reports are stil type(str)
    assert isinstance(control_msg.control.connectorConfig.config["access_token"], str)
    # new custom_reports are type(list)
    assert isinstance(control_msg.control.connectorConfig.config["credentials"]["access_token"], str)
    # check the migrated values
    assert control_msg.control.connectorConfig.config["credentials"]["access_token"] == "******"
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "credentials" not in test_config
    # check the old property is still there
    assert "access_token" in test_config
    assert isinstance(test_config["access_token"], str)


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    migration_instance = MigrateAccessTokenToCredentials()
    assert not migration_instance.should_migrate(new_config)


def test_should_not_migrate_upgraded_config():
    new_config = load_config(UPGRADED_TEST_CONFIG_PATH)
    migration_instance = MigrateAccessTokenToCredentials()
    assert not migration_instance.should_migrate(new_config)

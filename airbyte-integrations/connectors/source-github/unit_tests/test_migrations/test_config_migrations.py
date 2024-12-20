#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import Any, Mapping

from source_github.config_migrations import MigrateBranch, MigrateRepository
from source_github.source import SourceGithub

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source


# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"
NEW_TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_new_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceGithub()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("repositories")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config():
    migration_instance = MigrateRepository
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "repositories" in test_migrated_config
    assert isinstance(test_migrated_config["repositories"], list)
    # check the old property is in place
    assert "repository" in test_migrated_config
    assert isinstance(test_migrated_config["repository"], str)
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # new repositories is of type(list)
    assert isinstance(control_msg.control.connectorConfig.config["repositories"], list)
    # check the migrated values
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migrated property
    assert "repositories" not in test_config
    assert "branches" not in test_config
    # check the old property is still there
    assert "repository" in test_config
    assert "branch" in test_config
    assert isinstance(test_config["repository"], str)
    assert isinstance(test_config["branch"], str)


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    for instance in MigrateBranch, MigrateRepository:
        assert not instance._should_migrate(new_config)

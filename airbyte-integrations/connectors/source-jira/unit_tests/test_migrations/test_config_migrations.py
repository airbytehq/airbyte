#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import Any, Mapping

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_jira.config_migrations import MigrateIssueExpandProperties
from source_jira.source import SourceJira

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceJira()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("issues_stream_expand_with")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config():
    migration_instance = MigrateIssueExpandProperties()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "issues_stream_expand_with" in test_migrated_config
    assert isinstance(test_migrated_config["issues_stream_expand_with"], list)
    # check the old property is in place
    assert all(key in test_migrated_config for key in migration_instance.migrate_from_keys_map)
    assert all(isinstance(test_migrated_config[key], bool) for key in migration_instance.migrate_from_keys_map)
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # check the migrated values
    assert control_msg.control.connectorConfig.config["issues_stream_expand_with"] == ["changelog", "renderedFields"]
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migrated property
    assert "issues_stream_expand_with" not in test_config
    # check the old property is still there
    assert all(key in test_config for key in MigrateIssueExpandProperties.migrate_from_keys_map)
    assert all(isinstance(test_config[key], bool) for key in MigrateIssueExpandProperties.migrate_from_keys_map)

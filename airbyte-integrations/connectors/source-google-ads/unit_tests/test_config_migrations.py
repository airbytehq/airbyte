#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_google_ads.config_migrations import MigrateCustomQuery
from source_google_ads.source import SourceGoogleAds

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/custom_query/test_config.json"
NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/custom_query/test_new_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceGoogleAds()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("custom_queries_array")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config():
    migration_instance = MigrateCustomQuery()
    original_config = load_config()
    original_config_queries = original_config["custom_queries"].copy()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "custom_queries_array" in test_migrated_config
    assert "segments.date" in test_migrated_config["custom_queries_array"][0]["query"]
    # check the old property is in place
    assert "custom_queries" in test_migrated_config
    assert test_migrated_config["custom_queries"] == original_config_queries
    assert "segments.date" not in test_migrated_config["custom_queries"][0]["query"]
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # load the old custom reports VS migrated
    new_config_queries = test_migrated_config["custom_queries_array"].copy()
    new_config_queries[0]["query"] = new_config_queries[0]["query"].replace(", segments.date", "")
    print(f"{original_config=} \n {test_migrated_config=}")
    assert original_config["custom_queries"] == new_config_queries
    # test CONTROL MESSAGE was emitted
    control_msg = migration_instance.message_repository._message_queue[0]
    assert control_msg.type == Type.CONTROL
    assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "custom_queries_array" not in test_config
    # check the old property is still there
    assert "custom_queries" in test_config


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    migration_instance = MigrateCustomQuery()
    assert not migration_instance.should_migrate(new_config)

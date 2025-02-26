#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from source_google_analytics_data_api.config_migrations import MigrateCustomReports
from source_google_analytics_data_api.source import SourceGoogleAnalyticsDataApi

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source


# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceGoogleAnalyticsDataApi()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("custom_reports_array")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config(capsys):
    migration_instance = MigrateCustomReports()
    original_config = load_config()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_migrated_config = load_config()
    # check migrated property
    assert "custom_reports_array" in test_migrated_config
    assert isinstance(test_migrated_config["custom_reports_array"], list)
    # check the old property is in place
    assert "custom_reports" in test_migrated_config
    assert isinstance(test_migrated_config["custom_reports"], str)
    # check the migration should be skipped, once already done
    assert not migration_instance._should_migrate(test_migrated_config)
    # load the old custom reports VS migrated
    assert json.loads(original_config["custom_reports"]) == test_migrated_config["custom_reports_array"]
    # test CONTROL MESSAGE was emitted
    control_msg = json.loads(capsys.readouterr().out)
    assert control_msg["type"] == Type.CONTROL.value
    assert control_msg["control"]["type"] == OrchestratorType.CONNECTOR_CONFIG.value
    # old custom_reports are stil type(str)
    assert isinstance(control_msg["control"]["connectorConfig"]["config"]["custom_reports"], str)
    # new custom_reports are type(list)
    assert isinstance(control_msg["control"]["connectorConfig"]["config"]["custom_reports_array"], list)
    # check the migrated values
    assert control_msg["control"]["connectorConfig"]["config"]["custom_reports_array"][0]["name"] == "custom_dimensions"
    assert control_msg["control"]["connectorConfig"]["config"]["custom_reports_array"][0]["dimensions"] == ["date", "country", "device"]
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted():
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "custom_reports_array" not in test_config
    # check the old property is still there
    assert "custom_reports" in test_config
    assert isinstance(test_config["custom_reports"], str)

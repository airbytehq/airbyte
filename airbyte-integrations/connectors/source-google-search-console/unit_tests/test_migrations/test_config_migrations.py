#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.sources import Source
from source_google_search_console.config_migrations import MigrateCustomReports
from source_google_search_console.source import SourceGoogleSearchConsole

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceGoogleSearchConsole()


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


def test_migrate_config():
    # migrate the test_config
    MigrateCustomReports.migrate(SOURCE_INPUT_ARGS, SOURCE)
    # load the updated config
    test_config = load_config()
    # check migrated property
    assert "custom_reports_array" in test_config
    assert isinstance(test_config["custom_reports_array"], list)
    # check the old property is in place
    assert "custom_reports" in test_config
    assert isinstance(test_config["custom_reports"], str)


def test_migrated_report_values_are_the_same():
    test_config = load_config()
    # load the old custom reports
    old_custom_reports = json.loads(test_config["custom_reports"])
    # load new custom reports
    migrated_custom_reports = test_config["custom_reports_array"]
    # compare
    assert old_custom_reports == migrated_custom_reports


def test_should_migrate_after_migration():
    assert not MigrateCustomReports.should_migrate(load_config())


def test_config_is_reverted():
    # revert the test_config to the starting point
    revert_migration()
    # check the test_config state, it has to be the same as before tests
    test_config = load_config()
    # check the config no longer has the migarted property
    assert "custom_reports_array" not in test_config
    # check the old property is still there
    assert "custom_reports" in test_config
    assert isinstance(test_config["custom_reports"], str)

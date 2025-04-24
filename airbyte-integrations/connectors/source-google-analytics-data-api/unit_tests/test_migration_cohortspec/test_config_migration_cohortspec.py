#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import Any, Mapping

import dpath.util
from source_google_analytics_data_api.config_migrations import MigrateCustomReportsCohortSpec
from source_google_analytics_data_api.source import SourceGoogleAnalyticsDataApi

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source


# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"
NEW_TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_new_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceGoogleAnalyticsDataApi()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_migrate_config(capsys):
    migration_instance = MigrateCustomReportsCohortSpec()
    # migrate the test_config
    migration_instance.migrate(SOURCE_INPUT_ARGS, SOURCE)

    what = capsys.readouterr().out
    control_msg = json.loads(what)
    assert control_msg["type"] == Type.CONTROL.value
    assert control_msg["control"]["type"] == OrchestratorType.CONNECTOR_CONFIG.value

    assert control_msg["control"]["connectorConfig"]["config"]["custom_reports_array"][0]["cohortSpec"]["enabled"] == "true"
    assert control_msg["control"]["connectorConfig"]["config"]["custom_reports_array"][1]["cohortSpec"]["enabled"] == "false"


def test_should_not_migrate_new_config():
    new_config = load_config(NEW_TEST_CONFIG_PATH)
    assert not MigrateCustomReportsCohortSpec._should_migrate(new_config)

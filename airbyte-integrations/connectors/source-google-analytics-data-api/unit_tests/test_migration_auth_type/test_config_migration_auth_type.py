#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
from typing import Any, Mapping

import pytest
from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_google_analytics_data_api.config_migrations import MigrateAuth
from source_google_analytics_data_api.source import SourceGoogleAnalyticsDataApi

# BASE ARGS
CMD = "check"
SERVICE_INVALID_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_invalid_service_config.json"
CLIENT_INVALID_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_invalid_client_config.json"
VALID_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_new_config.json"
SOURCE: Source = SourceGoogleAnalyticsDataApi()


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


@pytest.mark.parametrize(
    "input_path,target_auth_type",
    (
        (SERVICE_INVALID_CONFIG_PATH, "Service"),
        (CLIENT_INVALID_CONFIG_PATH, "Client")
    )
)
def test_migrate_config(capsys, input_path, target_auth_type):
    migration_instance = MigrateAuth()
    source_input_args = [CMD, "--config", input_path]
    migration_instance.migrate(source_input_args, SOURCE)

    what = capsys.readouterr().out
    control_msg = json.loads(what)
    assert control_msg["type"] == Type.CONTROL.value
    assert control_msg["control"]["type"] == OrchestratorType.CONNECTOR_CONFIG.value

    assert control_msg["control"]["connectorConfig"]["config"]["credentials"]["auth_type"] == target_auth_type


def test_should_not_migrate_new_config():
    new_config = load_config(VALID_CONFIG_PATH)
    assert not MigrateAuth._should_migrate(new_config)

# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os
from typing import Any, Mapping

from airbyte_cdk.test.entrypoint_wrapper import _run_command
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source, get_stream_by_name


CMD = "check"
TEST_CONFIG_LEGACY_PATH = f"{os.path.dirname(__file__)}/configs/legacy_config.json"
TEST_CONFIG_ACTUAL_PATH = f"{os.path.dirname(__file__)}/configs/actual_config.json"

SOURCE_INPUT_ARGS_LEGACY = [CMD, "--config", TEST_CONFIG_LEGACY_PATH]
SOURCE_INPUT_ARGS_ACTUAL = [CMD, "--config", TEST_CONFIG_ACTUAL_PATH]


def load_config(config_path: str = TEST_CONFIG_LEGACY_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_config_migration(requests_mock):
    requests_mock.get(
        "https://slack.com/api/users.list?limit=1000",
        json={"users": [{"id": 1}]},
        status_code=200,
    )

    state = StateBuilder().build()
    source = get_source(config=load_config(), state=state)
    output = _run_command(source=source, args=SOURCE_INPUT_ARGS_LEGACY)
    assert len([log for log in output.logs if log.log.message == "Check succeeded"]) == 1


def test_config_not_migrated(requests_mock):
    requests_mock.get(
        "https://slack.com/api/users.list?limit=1000",
        json={"users": [{"id": 1}]},
        status_code=200,
    )
    state = StateBuilder().build()
    source = get_source(config=load_config(TEST_CONFIG_ACTUAL_PATH), state=state)
    output = _run_command(source=source, args=SOURCE_INPUT_ARGS_LEGACY)
    assert len([log for log in output.logs if log.log.message == "Check succeeded"]) == 1

#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from source_amplitude import SourceAmplitude
from source_amplitude.api import ActiveUsers, Annotations, AverageSessionLength, Cohorts, Events


def get_config(config_path: str = "secrets/config.json") -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open(config_path, "r") as f:
        return json.loads(f.read())


# using real config from secrets/config_oauth.json
TEST_CONFIG: dict = get_config()
TEST_INSTANCE: object = SourceAmplitude()


def test_convert_auth_to_token():
    expected = "YWJjOmRlZg=="
    actual = TEST_INSTANCE._convert_auth_to_token("abc", "def")
    assert actual == expected


def test_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    actual = TEST_INSTANCE.check(logger=AirbyteLogger, config=TEST_CONFIG)
    assert actual == expected


@pytest.mark.parametrize(
    "expected_stream_cls",
    [
        (Cohorts),
        (Annotations),
        (ActiveUsers),
        (AverageSessionLength),
        (Events),
    ],
    ids=["Cohorts", "Annotations", "ActiveUsers", "AverageSessionLength", "Events"],
)
def test_streams(expected_stream_cls):
    streams = TEST_INSTANCE.streams(config=TEST_CONFIG)
    for stream in streams:
        if expected_stream_cls in streams:
            assert isinstance(stream, expected_stream_cls)

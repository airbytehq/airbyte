#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pendulum
import pytest
import requests
from airbyte_cdk import AirbyteLogger
from source_amplitude import SourceAmplitude
from source_amplitude.api import ActiveUsers, Annotations, AverageSessionLength, Cohorts, Events

TEST_CONFIG: dict = {
    "data_region": "test_data_region",
    "api_key": "test_api_key",
    "secret_key": "test_secret_key",
    "start_date": "2022-05-01T00:00:00Z"
}
TEST_INSTANCE: SourceAmplitude = SourceAmplitude()


class MockRequest:
    def __init__(self, status_code):
        self.status_code = status_code


def test_convert_auth_to_token():
    expected = "dXNlcm5hbWU6cGFzc3dvcmQ="
    actual = TEST_INSTANCE._convert_auth_to_token("username", "password")
    assert actual == expected


@pytest.mark.parametrize(
    "response, check_passed",
    [
        ({"id": 123}, True),
        (requests.HTTPError(), False),
    ],
    ids=["Success", "Fail"],
)
def test_check(response, check_passed):
    with patch.object(Cohorts, "read_records", return_value=response) as mock_method:
        result = TEST_INSTANCE.check_connection(logger=AirbyteLogger, config=TEST_CONFIG)
        mock_method.assert_called()
        assert check_passed == result[0]


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
    TEST_CONFIG["start_date"] = pendulum.tomorrow().to_datetime_string()
    streams = TEST_INSTANCE.streams(config=TEST_CONFIG)
    for stream in streams:
        if expected_stream_cls in streams:
            assert isinstance(stream, expected_stream_cls)


def test_validate_start_date():
    start_date = pendulum.tomorrow().to_datetime_string()
    now = pendulum.now().to_datetime_string()
    assert TEST_INSTANCE._validate_start_date(start_date).to_datetime_string() == now

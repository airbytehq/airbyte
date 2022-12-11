#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_openweather.source import SourceOpenWeather
from source_openweather.streams import OneCall


@pytest.mark.parametrize(
    "response_status",
    [200, 400],
)
def test_check_connection(mocker, response_status):
    validate_mock = mocker.patch("source_openweather.extra_validations.validate")
    validate_mock.return_value = {"appid": "test_appid", "lat": 1.0, "lon": 1.0, "lang": None, "units": None}
    requests_get_mock = mocker.patch("source_openweather.source.requests.get")
    requests_get_mock.return_value.status_code = response_status
    logger_mock = MagicMock()
    config_mock = MagicMock()

    source = SourceOpenWeather()
    if response_status == 200:
        assert source.check_connection(logger_mock, config_mock) == (True, None)
    else:
        assert source.check_connection(logger_mock, config_mock) == (False, requests_get_mock.return_value.json.return_value.get("message"))
    validate_mock.assert_called_with(config_mock)
    requests_get_mock.assert_called_with(
        "https://api.openweathermap.org/data/3.0/onecall", params={"appid": "test_appid", "lat": 1.0, "lon": 1.0}
    )


def test_check_connection_validation_error(mocker):
    validate_mock = mocker.patch("source_openweather.extra_validations.validate")
    error = Exception("expected message")
    validate_mock.side_effect = error
    logger_mock = MagicMock()

    source = SourceOpenWeather()
    assert source.check_connection(logger_mock, {}) == (False, error)


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OneCall, "__abstractmethods__", set())


def test_streams(patch_base_class, mocker):
    config_mock = MagicMock()
    validate_mock = mocker.patch("source_openweather.source.extra_validations.validate")
    source = SourceOpenWeather()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
    validate_mock.assert_called_with(config_mock)

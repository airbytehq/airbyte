#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_insightly.source import SourceInsightly


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("Bad things happened")


def mocked_requests_get(fail=False):
    def wrapper(*args, **kwargs):
        if fail:
            return MockResponse(None, 404)

        return MockResponse(
            {"INSTANCE_NAME": "bossco", "INSTANCE_SUBDOMAIN": None, "PLAN_NAME": "Gratis", "NEW_USER_EXPERIENCE_ENABLED": True}, 200
        )

    return wrapper


@patch("requests.get", side_effect=mocked_requests_get())
def test_check_connection(mocker):
    source = SourceInsightly()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@patch("requests.get", side_effect=mocked_requests_get(fail=True))
def test_check_connection_fail(mocker):
    source = SourceInsightly()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock)[0] is False
    assert source.check_connection(logger_mock, config_mock)[1] is not None


def test_streams(mocker):
    source = SourceInsightly()
    config_mock = MagicMock()
    streams = source.streams(config_mock)

    expected_streams_number = 37
    assert len(streams) == expected_streams_number

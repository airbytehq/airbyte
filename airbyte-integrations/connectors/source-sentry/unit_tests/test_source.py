#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.logger import AirbyteLogger
from source_sentry.source import SourceSentry
from source_sentry.streams import Events


def test_source_wrong_credentials(requests_mock):
    source = SourceSentry()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"auth_token": "test_auth_token"})
    assert not status


def test_check_connection(mocker):
    source = SourceSentry()
    logger_mock, config_mock = MagicMock(), MagicMock()
    mocker.patch.object(Events, "read_records", return_value=iter([{"id": "1", "name": "test"}]))
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceSentry()
    config_mock = MagicMock()
    config_mock["auth_token"] = "test-token"
    config_mock["organization"] = "test-organization"
    config_mock["project"] = "test-project"
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number

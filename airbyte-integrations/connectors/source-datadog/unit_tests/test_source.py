#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from source_datadog.source import SourceDatadog

logger = AirbyteLogger()


def test_check_connection_ok(config, mock_stream, mock_responses):
    mock_stream("dashboard", response=mock_responses.get("Dashboards"))
    ok, error_msg = SourceDatadog().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_exception(config, mock_stream, mock_responses):
    mock_stream("invalid_path", response=mock_responses.get("Dashboards"))
    ok, error_msg = SourceDatadog().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_empty_config(config):
    config = {}

    ok, error_msg = SourceDatadog().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_invalid_config(config):
    config.pop("api_key")

    ok, error_msg = SourceDatadog().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(config):
    streams = SourceDatadog().streams(config)

    assert len(streams) == 9


def test_spec():
    logger_mock = MagicMock()
    spec = SourceDatadog().spec(logger_mock)

    assert isinstance(spec, ConnectorSpecification)

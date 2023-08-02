#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification
from source_datadog.source import SourceDatadog
from source_datadog.streams import AuditLogs, SeriesStream

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


def test_streams_with_valid_queries(config_timeseries):
    streams = SourceDatadog().streams(config_timeseries)

    assert len(streams) == 11
    assert isinstance(streams[0], AuditLogs)
    assert isinstance(streams[-1], SeriesStream)
    assert streams[-1].name == "Resource"
    assert streams[-2].name == "NodeCount"


def test_streams_with_invalid_queries(config_timeseries_invalid, caplog):
    with caplog.at_level(logging.INFO):
        streams = SourceDatadog().streams(config_timeseries_invalid)

    assert len(streams) == 9
    assert isinstance(streams[0], AuditLogs)

    invalid_query_names = ["", "MissingQuery"]
    invalid_queries_exist = any(isinstance(stream, SeriesStream) and stream.name in invalid_query_names for stream in streams)
    assert not invalid_queries_exist

    missing_query_logs = "Query fields are missing, Streams not created"
    assert missing_query_logs in caplog.messages
    assert len(caplog.records) == 3

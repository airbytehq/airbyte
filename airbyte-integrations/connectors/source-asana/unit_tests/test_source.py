#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import PropertyMock, patch

from airbyte_cdk.logger import AirbyteLogger
from source_asana.source import SourceAsana

logger = AirbyteLogger()


def test_check_connection_ok(config, mock_stream, mock_response):
    mock_stream("workspaces", response=mock_response)
    ok, error_msg = SourceAsana().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(config):
    config = {}

    ok, error_msg = SourceAsana().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_exception(config):
    with patch("source_asana.streams.Workspaces.use_cache", new_callable=PropertyMock, return_value=False):
        ok, error_msg = SourceAsana().check_connection(logger, config=config)

        assert not ok
        assert error_msg


def test_streams(config):
    streams = SourceAsana().streams(config)

    assert len(streams) == 10

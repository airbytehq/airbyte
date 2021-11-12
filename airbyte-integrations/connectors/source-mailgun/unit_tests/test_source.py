#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Dict, Any
from unittest.mock import MagicMock

from source_mailgun.source import SourceMailgun


def test_check_connection(test_config: Dict[str, Any]):
    source = SourceMailgun()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceMailgun()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number

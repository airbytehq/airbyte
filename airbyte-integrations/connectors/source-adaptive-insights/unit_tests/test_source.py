#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_adaptive_insights.source import SourceAdaptiveInsights


def test_check_connection(requests_mock):
    expected = """<?xml version="1.0" encoding="UTF-8"?>
    <response success="true">
    </response>
    """
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=expected)
    source = SourceAdaptiveInsights()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceAdaptiveInsights()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
    pass

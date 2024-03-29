#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_survey_monkey_demo.source import SourceSurveyMonkeyDemo


def test_check_connection(mocker):
    source = SourceSurveyMonkeyDemo()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceSurveyMonkeyDemo()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number

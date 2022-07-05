#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_pivotal_tracker.source import SourcePivotalTracker


@responses.activate
def test_check_connection(config_pass, projects_response):
    source = SourcePivotalTracker()
    logger_mock = MagicMock()
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects", json=projects_response)
    assert source.check_connection(logger_mock, config_pass) == (True, None)


@responses.activate
def test_streams(config_pass, projects_response):
    source = SourcePivotalTracker()
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects", json=projects_response)
    streams = source.streams(config_pass)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number

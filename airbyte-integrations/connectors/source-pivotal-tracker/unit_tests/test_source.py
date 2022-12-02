#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_pivotal_tracker.source import SourcePivotalTracker


@responses.activate
def test_check_connection(config_pass, projects_response, project_detail_response):
    source = SourcePivotalTracker()
    logger_mock = MagicMock()
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects", json=projects_response)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/98", json=project_detail_response)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/99", json=project_detail_response)
    assert source.check_connection(logger_mock, config_pass) == (True, None)


@responses.activate
def test_streams(config_pass, projects_response, project_detail_response):
    source = SourcePivotalTracker()
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects", json=projects_response)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/98", json=project_detail_response)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/99", json=project_detail_response)
    streams = source.streams(config_pass)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number


@responses.activate
def test_project_availability(config_pass, project_detail_response):
    source = SourcePivotalTracker()
    auth = source._get_authenticator(config_pass)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/98", json=project_detail_response)
    responses.add(responses.GET, "https://www.pivotaltracker.com/services/v5/projects/99", json={}, status=403)
    response = source._check_project_availability(auth, 98)
    assert response

    response = source._check_project_availability(auth, 99)
    assert not response

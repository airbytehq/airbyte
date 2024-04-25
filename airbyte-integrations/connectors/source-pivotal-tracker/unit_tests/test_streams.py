#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_pivotal_tracker.source import SourcePivotalTracker

CONFIG = {
  "api_token": "good"
}
stream_slice = {"project_id": 99}


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourcePivotalTracker()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


def get_projects_mock(requests_mock, projects_response):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    for json in projects_response:
        requests_mock.get("projects", json=json)


def set_test_stream(requests_mock, projects_response, stream_name, stream_response, endpoint_suffix):
    base_url = "https://www.pivotaltracker.com/services/v5/projects/99/"
    endpoint_url = base_url + endpoint_suffix
    expected_record = dict(stream_response[0])

    requests_mock.get(url=endpoint_url, status_code=200)
    stream = get_stream_by_name(stream_name, CONFIG)
    get_projects_mock(requests_mock, projects_response)

    for json_data in stream_response:
        requests_mock.get(endpoint_url, json=json_data)

    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


def test_projects(requests_mock, projects_response):
    stream = get_stream_by_name("projects", CONFIG)
    expected_record = dict(projects_response[0])
    get_projects_mock(requests_mock, projects_response)
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


def test_project_memberships(requests_mock, projects_response, project_memberships_response):
    set_test_stream(requests_mock, projects_response, "project_memberships", project_memberships_response, "memberships")


def test_activity(requests_mock, projects_response, activity_response):
    set_test_stream(requests_mock, projects_response, "activity", activity_response, "activity")


def test_labels(requests_mock, projects_response, labels_response):
    set_test_stream(requests_mock, projects_response, "labels", labels_response, "labels")


def test_releases(requests_mock, projects_response, releases_response):
    set_test_stream(requests_mock, projects_response, "releases", releases_response, "releases")


def test_epics(requests_mock, projects_response, epics_response):
    set_test_stream(requests_mock, projects_response, "epics", epics_response, "epics")


def test_stories(requests_mock, projects_response, stories_response):
    set_test_stream(requests_mock, projects_response, "stories", stories_response, "stories")


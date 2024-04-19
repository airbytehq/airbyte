#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from pytest import fixture
from typing import Any, Mapping
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from source_pivotal_tracker.source import SourcePivotalTracker

CONFIG = {
  "api_token": "good"
}
stream_slice = {"project_id": 99}

def load_file(fn):
    return open(os.path.join("unit_tests", "responses", fn)).read()


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourcePivotalTracker()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


projects_mock = json.loads(load_file("projects.json"))
def test_projects(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    stream = get_stream_by_name("projects", CONFIG)
    expected_record = dict(projects_mock[0])
    for json in projects_mock:
        requests_mock.get("projects", json=json)

    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


project_memberships_mock = json.loads(load_file("project_memberships.json"))
def test_project_memberships(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/memberships", status_code=200)
    stream = get_stream_by_name("project_memberships", CONFIG)
    expected_record = dict(project_memberships_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in project_memberships_mock:
        requests_mock.get("project_memberships", json=json)

    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


activity_mock = json.loads(load_file("activity.json"))
def test_activity(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/activity", status_code=200)
    stream = get_stream_by_name("activity", CONFIG)
    expected_record = dict(activity_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in activity_mock:
        requests_mock.get("activity", json=json)

    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


labels_mock = json.loads(load_file("labels.json"))
def test_labels(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/labels", status_code=200)
    stream = get_stream_by_name("labels", CONFIG)
    expected_record = dict(labels_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in labels_mock:
        requests_mock.get("labels", json=json)
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            count += 1
            assert dict(record) == expected_record


releases_mock = json.loads(load_file("releases.json"))
def test_releases(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/releases", status_code=200)
    stream = get_stream_by_name("releases", CONFIG)
    expected_record = dict(releases_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in releases_mock:
        requests_mock.get("releases", json=json)
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


epics_mock = json.loads(load_file("epics.json"))
def test_epics(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/epics", status_code=200)
    stream = get_stream_by_name("epics", CONFIG)
    expected_record = dict(epics_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in epics_mock:
        requests_mock.get("epics", json=json)
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record
        

stories_mock = json.loads(load_file("stories.json"))
def test_stories(requests_mock):
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects", status_code=200)
    requests_mock.get(url="https://www.pivotaltracker.com/services/v5/projects/99/stories", status_code=200)
    stream = get_stream_by_name("stories", CONFIG)
    expected_record = dict(stories_mock[0])
    for json in projects_mock:
        requests_mock.get("project", json=json)
    for json in stories_mock:
        requests_mock.get("stories", json=json)
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record

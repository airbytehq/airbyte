#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import responses
from airbyte_cdk.models import SyncMode
from source_pivotal_tracker.source import Activity, Epics, Labels, PivotalAuthenticator, ProjectMemberships, Projects, Releases, Stories

auth = PivotalAuthenticator("goodtoken")
project_args = {"project_ids": [98, 99], "authenticator": auth}
stream_slice = {"project_id": 99}


@responses.activate
def test_projects_stream(projects_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects",
        json=projects_response,
    )
    stream = Projects(authenticator=auth)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, None, None)]
    assert len(records) == 2
    assert len(responses.calls) == 1


@responses.activate
def test_project_memberships_stream(project_memberships_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/memberships",
        json=project_memberships_response,
    )
    stream = ProjectMemberships(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 7
    assert len(responses.calls) == 1


@responses.activate
def test_activity_stream(activity_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/activity",
        json=activity_response,
    )
    stream = Activity(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 15
    assert len(responses.calls) == 1


@responses.activate
def test_labels_stream(labels_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/labels",
        json=labels_response,
    )
    stream = Labels(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 10
    assert len(responses.calls) == 1


@responses.activate
def test_releases_stream(releases_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/releases",
        json=releases_response,
    )
    stream = Releases(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 1
    assert len(responses.calls) == 1


@responses.activate
def test_epics_stream(epics_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/epics",
        json=epics_response,
    )
    stream = Epics(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_stories_stream(stories_response):
    responses.add(
        responses.GET,
        "https://www.pivotaltracker.com/services/v5/projects/99/stories",
        json=stories_response,
    )
    stream = Stories(**project_args)
    records = [r for r in stream.read_records(SyncMode.full_refresh, None, stream_slice, None)]
    assert len(records) == 4
    assert len(responses.calls) == 1

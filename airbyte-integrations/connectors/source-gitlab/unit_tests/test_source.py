#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

from source_gitlab import SourceGitlab
from source_gitlab.streams import GitlabStream


def test_streams(config, requests_mock):
    requests_mock.get("/api/v4/groups", json=[{"id": "g1"}, {"id": "g256"}])
    source = SourceGitlab()
    streams = source.streams(config)
    assert len(streams) == 22
    assert all([isinstance(stream, GitlabStream) for stream in streams])
    groups, projects, *_ = streams
    assert groups.group_ids == ["g1", "g256"]
    assert projects.project_ids == []


def test_connection_success(config, requests_mock):
    requests_mock.get("/api/v4/groups", json=[{"id": "g1"}])
    requests_mock.get("/api/v4/groups/g1", json=[{"id": "g1", "projects": [{"id": "p1", "path_with_namespace": "p1"}]}])
    requests_mock.get("/api/v4/projects/p1", json={"id": "p1"})
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert (status, msg) == (True, None)


def test_connection_fail(config, mocker, requests_mock):
    mocker.patch("time.sleep")
    requests_mock.get("/api/v4/groups", status_code=500)
    source = SourceGitlab()
    status, msg = source.check_connection(logging.getLogger(), config)
    assert status is False, msg.startswith('Unable to connect to Gitlab API with the provided credentials - "DefaultBackoffException"')

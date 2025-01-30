#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import pytest
from conftest import BASE_CONFIG, GROUPS_LIST_URL, get_stream_by_name

from airbyte_cdk.models import SyncMode


CONFIG = BASE_CONFIG | {"projects_list": ["p_1"]}


@pytest.mark.parametrize(
    ("stream_name", "extra_mocks"),
    (
        ("projects", ({"url": "/api/v4/projects/p_1", "status_code": 403},)),
        (
            "branches",
            (
                {"url": "/api/v4/projects/p_1", "json": [{"id": "p_1"}]},
                {"url": "/api/v4/projects/p_1/repository/branches", "status_code": 403},
            ),
        ),
    ),
)
def test_should_retry(requests_mock, stream_name, extra_mocks):
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    stream = get_stream_by_name(stream_name, CONFIG)
    for extra_mock in extra_mocks:
        requests_mock.get(**extra_mock)

    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        records.extend(list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
    assert records == []
    assert requests_mock.call_count == len(extra_mocks) + 1


test_cases = (
    (
        "jobs",
        (
            ("/api/v4/projects/p_1/pipelines", [{"project_id": "p_1", "id": "build_project_p1"}]),
            (
                "/api/v4/projects/p_1/pipelines/build_project_p1/jobs",
                [
                    {
                        "id": "j_1",
                        "user": {"id": "u_1"},
                        "pipeline": {"id": "p_17"},
                        "runner": None,
                        "commit": {"id": "c_23"},
                    },
                ],
            ),
        ),
        {
            "commit": {"id": "c_23"},
            "commit_id": "c_23",
            "id": "j_1",
            "pipeline": {"id": "p_17"},
            "pipeline_id": "p_17",
            "project_id": "p_1",
            "runner": None,
            "runner_id": None,
            "user": {"id": "u_1"},
            "user_id": "u_1",
        },
    ),
    (
        "tags",
        (("/api/v4/projects/p_1/repository/tags", [{"commit": {"id": "c_1"}, "name": "t_1", "target": "ddc89"}]),),
        {"commit": {"id": "c_1"}, "commit_id": "c_1", "project_id": "p_1", "name": "t_1", "target": "ddc89"},
    ),
    (
        "releases",
        (
            (
                "/api/v4/projects/p_1/releases",
                [
                    {
                        "id": "r_1",
                        "author": {"name": "John", "id": "john"},
                        "commit": {"id": "abcd689"},
                        "milestones": [{"id": "m1", "title": "Q1"}, {"id": "m2", "title": "Q2"}],
                    }
                ],
            ),
        ),
        {
            "author": {"id": "john", "name": "John"},
            "author_id": "john",
            "commit": {"id": "abcd689"},
            "commit_id": "abcd689",
            "id": "r_1",
            "milestones": ["m1", "m2"],
            "project_id": "p_1",
        },
    ),
    (
        "deployments",
        (
            (
                "/api/v4/projects/p_1/deployments",
                [
                    {
                        "id": "r_1",
                        "user": {"name": "John", "id": "john_123", "username": "john"},
                        "environment": {"name": "dev"},
                        "commit": {"id": "abcd689"},
                    }
                ],
            ),
        ),
        {
            "id": "r_1",
            "user": {"name": "John", "id": "john_123", "username": "john"},
            "environment": {"name": "dev"},
            "commit": {"id": "abcd689"},
            "user_id": "john_123",
            "environment_id": None,
            "user_username": "john",
            "user_full_name": "John",
            "environment_name": "dev",
            "project_id": "p_1",
        },
    ),
    (
        "merge_request_commits",
        (
            ("/api/v4/projects/p_1/merge_requests", [{"id": "mr_1", "iid": "mr_1", "project_id": "p_1"}]),
            ("/api/v4/projects/p_1/merge_requests/mr_1/commits", [{"id": "mrc_1"}]),
        ),
        {"id": "mrc_1", "project_id": "p_1", "merge_request_iid": "mr_1"},
    ),
)


@pytest.mark.parametrize(("stream_name", "response_mocks", "expected_record"), test_cases)
def test_transform(requests_mock, stream_name, response_mocks, expected_record):
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    stream = get_stream_by_name(stream_name, CONFIG)
    requests_mock.get("/api/v4/projects/p_1", json=[{"id": "p_1"}])

    for url, json in response_mocks:
        requests_mock.get(url, json=json)

    for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh):
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            assert dict(record) == expected_record


def test_stream_slices_child_stream(requests_mock):
    commits = get_stream_by_name("commits", CONFIG)
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    requests_mock.get(
        url="https://gitlab.com/api/v4/projects/p_1?per_page=50&statistics=1",
        json=[{"id": 13082000, "description": "", "name": "New CI Test Project"}],
    )
    stream_state = {"13082000": {"" "created_at": "2021-03-10T23:58:1213"}}

    slices = list(commits.stream_slices(sync_mode=SyncMode.full_refresh, stream_state=stream_state))
    assert slices


def test_request_params():
    commits = get_stream_by_name("commits", CONFIG)
    assert commits.retriever.requester.get_request_params() == {"with_stats": "true"}

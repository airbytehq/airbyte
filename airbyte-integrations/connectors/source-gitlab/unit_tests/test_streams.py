#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_gitlab.streams import Branches, Commits, Jobs, MergeRequestCommits, MergeRequests, Pipelines, Projects, Releases, Tags

auth_params = {"authenticator": NoAuth(), "api_url": "gitlab.com"}
start_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)


@pytest.fixture()
def projects():
    return Projects(project_ids=["p_1"], **auth_params)


@pytest.fixture()
def pipelines(projects):
    return Pipelines(parent_stream=projects, start_date=str(start_date), **auth_params)


@pytest.fixture()
def merge_requests(projects):
    return MergeRequests(parent_stream=projects, start_date=str(start_date), **auth_params)


@pytest.fixture()
def tags(projects):
    return Tags(parent_stream=projects, repository_part=True, **auth_params)


@pytest.fixture()
def releases(projects):
    return Releases(parent_stream=projects, **auth_params)


@pytest.fixture()
def jobs(pipelines):
    return Jobs(parent_stream=pipelines, **auth_params)


@pytest.fixture()
def merge_request_commits(merge_requests):
    return MergeRequestCommits(parent_stream=merge_requests, **auth_params)


@pytest.fixture()
def branches(projects):
    return Branches(parent_stream=projects, **auth_params)


@pytest.fixture()
def commits(projects):
    return Commits(parent_stream=projects, repository_part=True, start_date=str(start_date), **auth_params)


@pytest.mark.parametrize(
    "stream, extra_mocks, expected_call_count",
    (
        (
            "projects",
            ({"url": "/api/v4/projects/p_1", "status_code": 403},),
            1
        ),
        (
            "projects",
            ({"url": "/api/v4/projects/p_1", "status_code": 404},),
            1
        ),
        (
            "branches",
            (
                {"url": "/api/v4/projects/p_1", "json": [{"id": "p_1"}]},
                {"url": "/api/v4/projects/p_1/branches", "status_code": 403}
            ),
            2
        ),
        (
            "branches",
            (
                {"url": "/api/v4/projects/p_1", "json": [{"id": "p_1"}]},
                {"url": "/api/v4/projects/p_1/branches", "status_code": 404}
            ),
            2
        ),
    ),
)
def test_should_retry(mocker, requests_mock, stream, extra_mocks, expected_call_count, request):
    mocker.patch("time.sleep")
    stream = request.getfixturevalue(stream)
    for extra_mock in extra_mocks:
        requests_mock.get(**extra_mock)

    for stream_slice in stream.stream_slices(sync_mode="full_refresh"):
        records = list(stream.read_records(sync_mode="full_refresh", stream_slice=stream_slice))
    assert records == []
    assert requests_mock.call_count == expected_call_count


test_cases = (
    (
        "jobs",
        (
            ("/api/v4/projects/p_1/pipelines", [{"project_id": "p_1", "id": "build_project_p1"}],),
            (
                "/api/v4/projects/p_1/pipelines/build_project_p1/jobs",
                [
                    {"id": "j_1", "user": {"id": "u_1"}, "pipeline": {"id": "p_17"}, "runner": None, "commit": {"id": "c_23"}}
                ]
            ),
        ),
        [{"commit": {"id": "c_23"}, "commit_id": "c_23", "id": "j_1", "pipeline": {"id": "p_17"}, "pipeline_id": "p_17", "project_id": "p_1", "runner": None, "runner_id": None, "user": {"id": "u_1"}, "user_id": "u_1"}]
    ),
    (
        "tags",
        (
            ("/api/v4/projects/p_1/repository/tags", [{"commit": {"id": "c_1"}, "name": "t_1", "target": "ddc89"}],),
        ),
        [{"commit": {"id": "c_1"}, "commit_id": "c_1", "project_id": "p_1", "name": "t_1", "target": "ddc89"}]
    ),
    (
        "releases",
        (
            (
                "/api/v4/projects/p_1/releases",
                [
                    {
                        "id": "r_1",
                        "author": {"name": "John", "id": "666"},
                        "commit": {"id": "abcd689"},
                        "milestones": [{"id": "m1", "title": "Q1"}, {"id": "m2", "title": "Q2"}]
                    }
                ],
            ),
        ),
        [{"author": {"id": "666", "name": "John"}, "author_id": "666", "commit": {"id": "abcd689"}, "commit_id": "abcd689", "id": "r_1", "milestones": ["m1", "m2"], "project_id": "p_1"}]
    ),
    (
        "merge_request_commits",
        (
            ("/api/v4/projects/p_1/merge_requests", [{"id": "mr_1", "iid": "mr_1", "project_id": "p_1"}],),
            ("/api/v4/projects/p_1/merge_requests/mr_1", [{"id": "mrc_1",}],),
        ),
        [{"id": "mrc_1", "project_id": "p_1", "merge_request_iid": "mr_1"}]
    )
)


@pytest.mark.parametrize("stream, response_mocks, expected_records", test_cases)
def test_transform(requests_mock, stream, response_mocks, expected_records, request):
    stream = request.getfixturevalue(stream)
    requests_mock.get("/api/v4/projects/p_1", json=[{"id": "p_1"}])

    for url, json in response_mocks:
        requests_mock.get(url, json=json)

    records_iter = iter(expected_records)
    for stream_slice in stream.stream_slices(sync_mode="full_refresh"):
        for record in stream.read_records(sync_mode="full_refresh", stream_slice=stream_slice):
            assert record == next(records_iter)


@pytest.mark.parametrize(
    "stream, current_state, latest_record, new_state",
    (
            (
                "pipelines",
                {"219445": {"updated_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"updated_at": "2021-03-11T08:56:40.001+02:00"}},
                {"project_id": "219445", "updated_at": "2022-12-16T00:12:41.005675+02:00"},
                {"219445": {"updated_at": "2022-12-16T00:12:41.005675+02:00"}, "211378": {"updated_at": "2021-03-11T08:56:40.001+02:00"}}
            ),
            (
                "pipelines",
                {"219445": {"updated_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"updated_at": "2021-03-11T08:56:40.012001+02:00"}},
                {"project_id": "211378", "updated_at": "2021-03-10T23:58:58.011+02:00"},
                {"219445": {"updated_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"updated_at": "2021-03-11T08:56:40.012001+02:00"}}
            ),
            (
                "pipelines",
                {},
                {"project_id": "211378", "updated_at": "2021-03-10T23:58:58.010001+02:00"},
                {"211378": {"updated_at": "2021-03-10T23:58:58.010001+02:00"}}
            ),
            (
                "commits",
                {"219445": {"created_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"created_at": "2021-03-11T08:56:40.001+02:00"}},
                {"project_id": "219445", "created_at": "2022-12-16T00:12:41.005675+02:00"},
                {"219445": {"created_at": "2022-12-16T00:12:41.005675+02:00"}, "211378": {"created_at": "2021-03-11T08:56:40.001+02:00"}}
            ),
            (
                "commits",
                {"219445": {"created_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"created_at": "2021-03-11T08:56:40.012001+02:00"}},
                {"project_id": "211378", "created_at": "2021-03-10T23:58:58.011+02:00"},
                {"219445": {"created_at": "2022-12-14T17:07:34.005675+02:00"}, "211378": {"created_at": "2021-03-11T08:56:40.012001+02:00"}}
            ),
            (
                "commits",
                {},
                {"project_id": "211378", "created_at": "2021-03-10T23:58:58.010001+02:00"},
                {"211378": {"created_at": "2021-03-10T23:58:58.010001+02:00"}}
            )
    )
)
def test_updated_state(stream, current_state, latest_record, new_state, request):
    stream = request.getfixturevalue(stream)
    assert stream.get_updated_state(current_state, latest_record) == new_state

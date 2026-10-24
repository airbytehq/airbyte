#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .conftest import BASE_CONFIG, GROUPS_LIST_URL, get_source, get_stream_by_name


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
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name=stream_name, config=migrated_config)
    for extra_mock in extra_mocks:
        requests_mock.get(**extra_mock)

    records = []
    for partition in stream.generate_partitions():
        records.extend(list(partition.read()))
    assert records == []
    assert requests_mock.call_count == len(extra_mocks) + 1


def test_retries_after_rate_limit_using_retry_after(requests_mock, mocker):
    rate_limiting_time = mocker.patch("airbyte_cdk.sources.streams.http.rate_limiting.time")
    sleep = rate_limiting_time.sleep
    requests_mock.get(url=GROUPS_LIST_URL, json=[])
    requests_mock.register_uri(
        "GET",
        "/api/v4/projects/p_1",
        [
            {
                "status_code": 429,
                "headers": {"Retry-After": "30", "RateLimit-Remaining": "1999"},
            },
            {"status_code": 200, "json": [{"id": "p_1"}]},
        ],
    )
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name="projects", config=migrated_config)

    records = [dict(record) for partition in stream.generate_partitions() for record in partition.read()]

    assert records == [{"id": "p_1"}]
    sleep.assert_called_once_with(31)


def test_retries_after_rate_limit_without_retry_after(requests_mock, mocker):
    rate_limiting_time = mocker.patch("airbyte_cdk.sources.streams.http.rate_limiting.time")
    sleep = rate_limiting_time.sleep
    requests_mock.get(url=GROUPS_LIST_URL, json=[])
    requests_mock.register_uri(
        "GET",
        "/api/v4/projects/p_1",
        [
            {"status_code": 429, "headers": {"RateLimit-Remaining": "1999"}},
            {"status_code": 200, "json": [{"id": "p_1"}]},
        ],
    )
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name="projects", config=migrated_config)

    records = [dict(record) for partition in stream.generate_partitions() for record in partition.read()]

    assert records == [{"id": "p_1"}]
    sleep.assert_called_once_with(11)


def test_rate_limit_fails_when_retry_after_exceeds_max_wait(requests_mock, mocker):
    rate_limiting_time = mocker.patch("airbyte_cdk.sources.streams.http.rate_limiting.time")
    sleep = rate_limiting_time.sleep
    requests_mock.get(url=GROUPS_LIST_URL, json=[])
    projects_request = requests_mock.register_uri(
        "GET",
        "/api/v4/projects/p_1",
        status_code=429,
        headers={"Retry-After": "5000", "RateLimit-Remaining": "1999"},
    )
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name="projects", config=migrated_config)

    with pytest.raises(AirbyteTracedException) as exc_info:
        [dict(record) for partition in stream.generate_partitions() for record in partition.read()]

    assert "greater than or equal to the maximum of 3660" in exc_info.value.internal_message
    sleep.assert_not_called()
    assert projects_request.call_count == 1


def test_rate_limit_fails_after_max_retries(requests_mock, mocker):
    rate_limiting_time = mocker.patch("airbyte_cdk.sources.streams.http.rate_limiting.time")
    sleep = rate_limiting_time.sleep
    requests_mock.get(url=GROUPS_LIST_URL, json=[])

    def always_rate_limited(_request, context):
        context.status_code = 429
        context.headers["Retry-After"] = "1"
        context.headers["RateLimit-Remaining"] = "1999"
        return '{"message": "Too many requests"}'

    projects_request = requests_mock.register_uri("GET", "/api/v4/projects/p_1", text=always_rate_limited)
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name="projects", config=migrated_config)

    with pytest.raises(AirbyteTracedException) as exc_info:
        [dict(record) for partition in stream.generate_partitions() for record in partition.read()]

    assert "Rate limit retry budget exhausted" in exc_info.value.internal_message
    assert projects_request.call_count == 11
    assert sleep.call_count == 10


test_cases = (
    (
        "jobs",
        (
            (
                "/api/v4/projects/p_1/pipelines",
                [{"project_id": "p_1", "id": "build_project_p1", "updated_at": "2021-03-18T12:51:06.000Z"}],
            ),
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
            "pipeline_updated_at": "2021-03-18T12:51:06.000Z",
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
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name=stream_name, config=migrated_config)
    requests_mock.get("/api/v4/projects/p_1", json=[{"id": "p_1"}])

    for url, json in response_mocks:
        requests_mock.get(url, json=json)

    for partition in stream.generate_partitions():
        for record in partition.read():
            assert dict(record) == expected_record


def test_epics_milestone_dates_are_normalized(requests_mock):
    requests_mock.get(url=GROUPS_LIST_URL, json=[{"id": 1}])
    requests_mock.get("/api/v4/groups/1", json={"id": 1})
    requests_mock.get(
        "/api/v4/groups/1/epics",
        json=[
            {
                "iid": 1,
                "due_date_from_milestones": "2022-12-30T00:00:00+00:00",
                "start_date_from_milestones": "2022-12-11T00:00:00+00:00",
                "due_date": "2022-12-30",
                "work_item_id": 146029705,
                "imported": False,
                "imported_from": "none",
            },
            {"iid": 2},
            {"iid": 3, "due_date_from_milestones": None},
        ],
    )
    source = get_source(config=BASE_CONFIG)
    migrated_config = source.configure(config=BASE_CONFIG, temp_dir="/not/a/real/path")
    epics = get_stream_by_name(source=source, stream_name="epics", config=migrated_config)

    records = [dict(record) for partition in epics.generate_partitions() for record in partition.read()]

    assert records[0]["due_date_from_milestones"] == "2022-12-30"
    assert records[0]["start_date_from_milestones"] == "2022-12-11"
    assert records[0]["due_date"] == "2022-12-30"
    assert records[0]["work_item_id"] == 146029705
    assert records[0]["imported"] is False
    assert records[0]["imported_from"] == "none"
    assert "due_date_from_milestones" not in records[1]
    assert "start_date_from_milestones" not in records[1]
    assert records[2]["due_date_from_milestones"] is None


def test_stream_slices_child_stream(requests_mock):
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    commits = get_stream_by_name(source=source, stream_name="commits", config=migrated_config)
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    requests_mock.get(
        url="https://gitlab.com/api/v4/projects/p_1?per_page=50&statistics=1",
        json=[{"id": 13082000, "description": "", "name": "New CI Test Project"}],
    )
    stream_state = {"13082000": {"created_at": "2021-03-10T23:58:1213"}}

    slices = list(map(lambda partition: partition.to_slice(), commits.generate_partitions()))
    assert slices


def test_request_params():
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    commits = get_stream_by_name(source=source, stream_name="commits", config=migrated_config)
    assert commits._stream_partition_generator._partition_factory._retriever.requester.get_request_params() == {"with_stats": "true"}

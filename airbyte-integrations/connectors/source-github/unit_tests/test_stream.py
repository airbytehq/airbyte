#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
import responses
from airbyte_cdk.sources.streams.http.exceptions import BaseBackoffException
from responses import matchers
from source_github.streams import (
    Commits,
    ProjectColumns,
    Projects,
    PullRequestCommentReactions,
    PullRequestCommits,
    PullRequests,
    Repositories,
    Teams,
)

from .utils import read_full_refresh, read_incremental

DEFAULT_BACKOFF_DELAYS = [5, 10, 20, 40, 80]


@responses.activate
@patch("time.sleep")
def test_internal_server_error_retry(time_mock):
    args = {"authenticator": None, "repositories": ["test_repo"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)
    stream_slice = {"repository": "test_repo", "id": "id"}

    time_mock.reset_mock()
    responses.add(
        "GET",
        "https://api.github.com/repos/test_repo/pulls/comments/id/reactions",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        json={"message": "Server Error"},
    )
    with pytest.raises(BaseBackoffException):
        list(stream.read_records(sync_mode="full_refresh", stream_slice=stream_slice))

    sleep_delays = [delay[0][0] for delay in time_mock.call_args_list]
    assert sleep_delays == DEFAULT_BACKOFF_DELAYS


@pytest.mark.parametrize(
    ("http_status", "response_text", "expected_backoff_time"),
    [
        (HTTPStatus.BAD_GATEWAY, "", 60),
    ],
)
def test_backoff_time(http_status, response_text, expected_backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    response_mock.text = response_text
    args = {"authenticator": None, "repositories": ["test_repo"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)
    assert stream.backoff_time(response_mock) == expected_backoff_time


@responses.activate
def test_stream_teams_404():
    kwargs = {"organizations": ["org_name"]}
    stream = Teams(**kwargs)

    responses.add(
        "GET",
        "https://api.github.com/orgs/org_name/teams",
        status=requests.codes.NOT_FOUND,
        json={"message": "Not Found", "documentation_url": "https://docs.github.com/rest/reference/teams#list-teams"},
    )

    assert read_full_refresh(stream) == []
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.github.com/orgs/org_name/teams?per_page=100"


@responses.activate
def test_stream_repositories_404():
    kwargs = {"organizations": ["org_name"]}
    stream = Repositories(**kwargs)

    responses.add(
        "GET",
        "https://api.github.com/orgs/org_name/repos",
        status=requests.codes.NOT_FOUND,
        json={"message": "Not Found", "documentation_url": "https://docs.github.com/rest/reference/repos#list-organization-repositories"},
    )

    assert read_full_refresh(stream) == []
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.github.com/orgs/org_name/repos?per_page=100"


@responses.activate
def test_stream_projects_disabled():
    kwargs = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["test_repo"]}
    stream = Projects(**kwargs)

    responses.add(
        "GET",
        "https://api.github.com/repos/test_repo/projects",
        status=requests.codes.GONE,
        json={"message": "Projects are disabled for this repository", "documentation_url": "https://docs.github.com/v3/projects"},
    )

    assert read_full_refresh(stream) == []
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.github.com/repos/test_repo/projects?per_page=100&state=all"


@responses.activate
def test_stream_pull_requests_incremental_read():

    page_size = 2
    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": page_size,
        "start_date": "2022-02-02T10:10:03Z",
    }

    stream = PullRequests(**repository_args_with_start_date)

    data = [
        {"id": 1, "updated_at": "2022-02-02T10:10:02Z"},
        {"id": 2, "updated_at": "2022-02-02T10:10:04Z"},
        {"id": 3, "updated_at": "2022-02-02T10:10:06Z"},
        {"id": 4, "updated_at": "2022-02-02T10:10:08Z"},
        {"id": 5, "updated_at": "2022-02-02T10:10:10Z"},
        {"id": 6, "updated_at": "2022-02-02T10:10:12Z"},
    ]

    api_url = "https://api.github.com/repos/organization/repository/pulls"

    responses.add(
        "GET",
        api_url,
        json=data[0:2],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=2>; rel="next"'},
        match=[matchers.query_param_matcher({"per_page": str(page_size), "direction": "asc"}, strict_match=False)],
    )

    responses.add(
        "GET",
        api_url,
        json=data[2:4],
        match=[matchers.query_param_matcher({"per_page": str(page_size), "direction": "asc", "page": "2"}, strict_match=False)],
    )

    responses.add(
        "GET",
        api_url,
        json=data[5:3:-1],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=2>; rel="next"'},
        match=[matchers.query_param_matcher({"per_page": str(page_size), "direction": "desc"}, strict_match=False)],
    )

    responses.add(
        "GET",
        api_url,
        json=data[3:1:-1],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=3>; rel="next"'},
        match=[matchers.query_param_matcher({"per_page": str(page_size), "direction": "desc", "page": "2"}, strict_match=False)],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [2, 3, 4]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:08Z"}}

    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [6, 5]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:12Z"}}


@responses.activate
def test_stream_commits_incremental_read():

    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-02T10:10:03Z",
    }

    default_branches = {"organization/repository": "master"}
    branches_to_pull = {"organization/repository": ["branch"]}

    stream = Commits(**repository_args_with_start_date, branches_to_pull=branches_to_pull, default_branches=default_branches)

    data = [
        {"sha": 1, "commit": {"author": {"date": "2022-02-02T10:10:02Z"}}},
        {"sha": 2, "commit": {"author": {"date": "2022-02-02T10:10:04Z"}}},
        {"sha": 3, "commit": {"author": {"date": "2022-02-02T10:10:06Z"}}},
        {"sha": 4, "commit": {"author": {"date": "2022-02-02T10:10:08Z"}}},
        {"sha": 5, "commit": {"author": {"date": "2022-02-02T10:10:10Z"}}},
    ]

    api_url = "https://api.github.com/repos/organization/repository/commits"

    responses.add(
        "GET",
        api_url,
        json=data[0:3],
        match=[matchers.query_param_matcher({"since": "2022-02-02T10:10:03Z", "sha": "branch"}, strict_match=False)],
    )

    responses.add(
        "GET",
        api_url,
        json=data[3:5],
        match=[matchers.query_param_matcher({"since": "2022-02-02T10:10:06Z", "sha": "branch"}, strict_match=False)],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert [r["sha"] for r in records] == [2, 3]
    assert stream_state == {"organization/repository": {"branch": {"created_at": "2022-02-02T10:10:06Z"}}}
    records = read_incremental(stream, stream_state)
    assert [r["sha"] for r in records] == [4, 5]
    assert stream_state == {"organization/repository": {"branch": {"created_at": "2022-02-02T10:10:10Z"}}}


@responses.activate
def test_stream_commits_state_upgrade():

    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-02T10:10:02Z",
    }

    default_branches = {"organization/repository": "master"}
    branches_to_pull = {"organization/repository": ["master"]}

    stream = Commits(**repository_args_with_start_date, branches_to_pull=branches_to_pull, default_branches=default_branches)

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/commits",
        json=[
            {"sha": 1, "commit": {"author": {"date": "2022-02-02T10:10:02Z"}}},
            {"sha": 2, "commit": {"author": {"date": "2022-02-02T10:10:04Z"}}},
        ],
        match=[matchers.query_param_matcher({"since": "2022-02-02T10:10:02Z", "sha": "master"}, strict_match=False)],
    )

    stream_state = {"organization/repository": {"created_at": "2022-02-02T10:10:02Z"}}
    records = read_incremental(stream, stream_state)
    assert [r["sha"] for r in records] == [2]
    assert stream_state == {"organization/repository": {"master": {"created_at": "2022-02-02T10:10:04Z"}}}


@responses.activate
def test_stream_pull_request_commits():

    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
    }
    repository_args_with_start_date = {**repository_args, "start_date": "2022-02-02T10:10:02Z"}

    stream = PullRequestCommits(PullRequests(**repository_args_with_start_date), **repository_args)

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls",
        json=[
            {"id": 1, "updated_at": "2022-02-02T10:10:02Z", "number": 1},
            {"id": 2, "updated_at": "2022-02-02T10:10:04Z", "number": 2},
            {"id": 3, "updated_at": "2022-02-02T10:10:06Z", "number": 3},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/2/commits",
        json=[{"sha": 1}, {"sha": 2}],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/3/commits",
        json=[{"sha": 3}, {"sha": 4}],
    )

    records = read_full_refresh(stream)
    assert records == [
        {"sha": 1, "repository": "organization/repository", "pull_number": 2},
        {"sha": 2, "repository": "organization/repository", "pull_number": 2},
        {"sha": 3, "repository": "organization/repository", "pull_number": 3},
        {"sha": 4, "repository": "organization/repository", "pull_number": 3},
    ]


@responses.activate
def test_stream_project_columns():

    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-01T00:00:00Z",
    }

    stream = ProjectColumns(Projects(**repository_args_with_start_date), **repository_args_with_start_date)

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/projects",
        json=[
            {"id": 1, "name": "project_1", "updated_at": "2022-01-01T10:00:00Z"},
            {"id": 2, "name": "project_2", "updated_at": "2022-03-01T10:00:00Z"},
            {"id": 3, "name": "project_3", "updated_at": "2022-05-01T10:00:00Z"},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/projects/2/columns",
        json=[
            {"id": 1, "name": "column_1", "updated_at": "2022-01-01T10:00:00Z"},
            {"id": 2, "name": "column_2", "updated_at": "2022-03-01T09:00:00Z"},
            {"id": 3, "name": "column_3", "updated_at": "2022-03-01T10:00:00Z"},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/projects/3/columns",
        json=[
            {"id": 1, "name": "column_1", "updated_at": "2022-01-01T10:00:00Z"},
            {"id": 2, "name": "column_2", "updated_at": "2022-05-01T10:00:00Z"},
        ],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state=stream_state)

    assert records == [
        {"id": 2, "name": "column_2", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T09:00:00Z"},
        {"id": 3, "name": "column_3", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T10:00:00Z"},
        {"id": 2, "name": "column_2", "project_id": 3, "repository": "organization/repository", "updated_at": "2022-05-01T10:00:00Z"},
    ]

    assert stream_state == {
        "organization/repository": {"2": {"updated_at": "2022-03-01T10:00:00Z"}, "3": {"updated_at": "2022-05-01T10:00:00Z"}}
    }

    responses.replace(
        "GET",
        "https://api.github.com/repos/organization/repository/projects",
        json=[
            {"id": 1, "name": "project_1", "updated_at": "2022-01-01T10:00:00Z"},
            {"id": 2, "name": "project_2", "updated_at": "2022-04-01T10:00:00Z"},
            {"id": 3, "name": "project_3", "updated_at": "2022-05-01T10:00:00Z"},
            {"id": 4, "name": "project_4", "updated_at": "2022-06-01T10:00:00Z"},
        ],
    )

    responses.replace(
        "GET",
        "https://api.github.com/projects/2/columns",
        json=[
            {"id": 1, "name": "column_1", "updated_at": "2022-01-01T10:00:00Z"},
            {"id": 2, "name": "column_2", "updated_at": "2022-03-01T09:00:00Z"},
            {"id": 3, "name": "column_3", "updated_at": "2022-03-01T10:00:00Z"},
            {"id": 4, "name": "column_4", "updated_at": "2022-04-01T10:00:00Z"},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/projects/4/columns",
        json=[
            {"id": 2, "name": "column_1", "updated_at": "2022-06-01T10:00:00Z"},
        ],
    )

    records = read_incremental(stream, stream_state=stream_state)

    assert records == [
        {"id": 4, "name": "column_4", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-04-01T10:00:00Z"},
        {"id": 2, "name": "column_1", "project_id": 4, "repository": "organization/repository", "updated_at": "2022-06-01T10:00:00Z"},
    ]

    assert stream_state == {
        "organization/repository": {
            "2": {"updated_at": "2022-04-01T10:00:00Z"},
            "3": {"updated_at": "2022-05-01T10:00:00Z"},
            "4": {"updated_at": "2022-06-01T10:00:00Z"},
        }
    }

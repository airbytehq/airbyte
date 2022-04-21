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
    Branches,
    Collaborators,
    Comments,
    CommitComments,
    Commits,
    Deployments,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    Organizations,
    ProjectCards,
    ProjectColumns,
    Projects,
    PullRequestCommentReactions,
    PullRequestCommits,
    PullRequests,
    Releases,
    Repositories,
    Reviews,
    Stargazers,
    Tags,
    TeamMembers,
    TeamMemberships,
    Teams,
    Users,
)

from .utils import ProjectsResponsesAPI, read_full_refresh, read_incremental, urlbase

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
@patch("time.sleep")
def test_retry_after(time_mock):
    stream = Organizations(organizations=["airbytehq"])
    responses.add("GET", "https://api.github.com/orgs/airbytehq", json={"login": "airbytehq"}, headers={"Retry-After": "10"})
    read_full_refresh(stream)
    assert time_mock.call_args[0][0] == 10
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.github.com/orgs/airbytehq?per_page=100"


@responses.activate
def test_stream_teams_404():
    organization_args = {"organizations": ["org_name"]}
    stream = Teams(**organization_args)

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
def test_stream_organizations_read():
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Organizations(**organization_args)
    responses.add("GET", "https://api.github.com/orgs/org1", json={"id": 1})
    responses.add("GET", "https://api.github.com/orgs/org2", json={"id": 2})
    records = read_full_refresh(stream)
    assert records == [{"id": 1}, {"id": 2}]


@responses.activate
def test_stream_teams_read():
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Teams(**organization_args)
    responses.add("GET", "https://api.github.com/orgs/org1/teams", json=[{"id": 1}, {"id": 2}])
    responses.add("GET", "https://api.github.com/orgs/org2/teams", json=[{"id": 3}])
    records = read_full_refresh(stream)
    assert records == [{"id": 1, "organization": "org1"}, {"id": 2, "organization": "org1"}, {"id": 3, "organization": "org2"}]
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == "https://api.github.com/orgs/org1/teams?per_page=100"
    assert responses.calls[1].request.url == "https://api.github.com/orgs/org2/teams?per_page=100"


@responses.activate
def test_stream_users_read():
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Users(**organization_args)
    responses.add("GET", "https://api.github.com/orgs/org1/members", json=[{"id": 1}, {"id": 2}])
    responses.add("GET", "https://api.github.com/orgs/org2/members", json=[{"id": 3}])
    records = read_full_refresh(stream)
    assert records == [{"id": 1, "organization": "org1"}, {"id": 2, "organization": "org1"}, {"id": 3, "organization": "org2"}]
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == "https://api.github.com/orgs/org1/members?per_page=100"
    assert responses.calls[1].request.url == "https://api.github.com/orgs/org2/members?per_page=100"


@responses.activate
def test_stream_repositories_404():
    organization_args = {"organizations": ["org_name"]}
    stream = Repositories(**organization_args)

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
def test_stream_repositories_read():
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Repositories(**organization_args)
    responses.add("GET", "https://api.github.com/orgs/org1/repos", json=[{"id": 1}, {"id": 2}])
    responses.add("GET", "https://api.github.com/orgs/org2/repos", json=[{"id": 3}])
    records = read_full_refresh(stream)
    assert records == [{"id": 1, "organization": "org1"}, {"id": 2, "organization": "org1"}, {"id": 3, "organization": "org2"}]
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == "https://api.github.com/orgs/org1/repos?per_page=100"
    assert responses.calls[1].request.url == "https://api.github.com/orgs/org2/repos?per_page=100"


@responses.activate
def test_stream_projects_disabled():

    repository_args_with_start_date = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["test_repo"]}

    stream = Projects(**repository_args_with_start_date)
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

    data = [
        {
            "updated_at": "2022-01-01T10:00:00Z",
        },
        {
            "updated_at": "2022-03-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-03-01T09:00:00Z"},
                {"updated_at": "2022-03-01T10:00:00Z"},
            ],
        },
        {
            "updated_at": "2022-05-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-05-01T10:00:00Z"},
            ],
        },
    ]

    ProjectsResponsesAPI.register(data)

    stream = ProjectColumns(Projects(**repository_args_with_start_date), **repository_args_with_start_date)

    stream_state = {}

    records = read_incremental(stream, stream_state=stream_state)

    assert records == [
        {"id": 22, "name": "column_22", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T09:00:00Z"},
        {"id": 23, "name": "column_23", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-03-01T10:00:00Z"},
        {"id": 32, "name": "column_32", "project_id": 3, "repository": "organization/repository", "updated_at": "2022-05-01T10:00:00Z"},
    ]

    assert stream_state == {
        "organization/repository": {"2": {"updated_at": "2022-03-01T10:00:00Z"}, "3": {"updated_at": "2022-05-01T10:00:00Z"}}
    }

    data = [
        {"updated_at": "2022-01-01T10:00:00Z"},
        {
            "updated_at": "2022-04-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-03-01T09:00:00Z"},
                {"updated_at": "2022-03-01T10:00:00Z"},
                {"updated_at": "2022-04-01T10:00:00Z"},
            ],
        },
        {
            "updated_at": "2022-05-01T10:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T10:00:00Z"},
                {"updated_at": "2022-05-01T10:00:00Z"},
            ],
        },
        {
            "updated_at": "2022-06-01T10:00:00Z",
            "columns": [{"updated_at": "2022-06-01T10:00:00Z"}],
        },
    ]

    ProjectsResponsesAPI.register(data)

    records = read_incremental(stream, stream_state=stream_state)
    assert records == [
        {"id": 24, "name": "column_24", "project_id": 2, "repository": "organization/repository", "updated_at": "2022-04-01T10:00:00Z"},
        {"id": 41, "name": "column_41", "project_id": 4, "repository": "organization/repository", "updated_at": "2022-06-01T10:00:00Z"},
    ]

    assert stream_state == {
        "organization/repository": {
            "2": {"updated_at": "2022-04-01T10:00:00Z"},
            "3": {"updated_at": "2022-05-01T10:00:00Z"},
            "4": {"updated_at": "2022-06-01T10:00:00Z"},
        }
    }


@responses.activate
def test_stream_project_cards():

    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-03-01T00:00:00Z",
    }

    projects_stream = Projects(**repository_args_with_start_date)
    project_columns_stream = ProjectColumns(projects_stream, **repository_args_with_start_date)
    stream = ProjectCards(project_columns_stream, **repository_args_with_start_date)

    data = [
        {
            "updated_at": "2022-01-01T00:00:00Z",
        },
        {
            "updated_at": "2022-06-01T00:00:00Z",
            "columns": [
                {
                    "updated_at": "2022-04-01T00:00:00Z",
                    "cards": [
                        {"updated_at": "2022-03-01T00:00:00Z"},
                        {"updated_at": "2022-04-01T00:00:00Z"},
                    ],
                },
                {"updated_at": "2022-05-01T09:00:00Z"},
                {
                    "updated_at": "2022-06-01T00:00:00Z",
                    "cards": [
                        {"updated_at": "2022-05-01T00:00:00Z"},
                        {"updated_at": "2022-06-01T00:00:00Z"},
                    ],
                },
            ],
        },
        {
            "updated_at": "2022-05-01T00:00:00Z",
            "columns": [
                {"updated_at": "2022-01-01T00:00:00Z"},
                {
                    "updated_at": "2022-05-01T00:00:00Z",
                    "cards": [
                        {"updated_at": "2022-02-01T00:00:00Z"},
                        {"updated_at": "2022-05-01T00:00:00Z"},
                    ],
                },
            ],
        },
    ]

    ProjectsResponsesAPI.register(data)

    stream_state = {}
    records = read_incremental(stream, stream_state=stream_state)

    assert records == [
        {
            "column_id": 21,
            "id": 212,
            "name": "card_212",
            "project_id": 2,
            "repository": "organization/repository",
            "updated_at": "2022-04-01T00:00:00Z",
        },
        {
            "column_id": 23,
            "id": 231,
            "name": "card_231",
            "project_id": 2,
            "repository": "organization/repository",
            "updated_at": "2022-05-01T00:00:00Z",
        },
        {
            "column_id": 23,
            "id": 232,
            "name": "card_232",
            "project_id": 2,
            "repository": "organization/repository",
            "updated_at": "2022-06-01T00:00:00Z",
        },
        {
            "column_id": 32,
            "id": 322,
            "name": "card_322",
            "project_id": 3,
            "repository": "organization/repository",
            "updated_at": "2022-05-01T00:00:00Z",
        },
    ]


@responses.activate
def test_stream_comments():

    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-02T10:10:03Z",
    }

    stream = Comments(**repository_args_with_start_date)

    data = [
        {"id": 1, "updated_at": "2022-02-02T10:10:02Z"},
        {"id": 2, "updated_at": "2022-02-02T10:10:04Z"},
        {"id": 3, "updated_at": "2022-02-02T10:10:06Z"},
        {"id": 4, "updated_at": "2022-02-02T10:10:08Z"},
    ]

    api_url = "https://api.github.com/repos/organization/repository/issues/comments"

    responses.add(
        "GET",
        api_url,
        json=data[0:2],
        match=[matchers.query_param_matcher({"since": "2022-02-02T10:10:03Z"}, strict_match=False)],
    )

    responses.add(
        "GET",
        api_url,
        json=data[2:4],
        match=[matchers.query_param_matcher({"since": "2022-02-02T10:10:04Z"}, strict_match=False)],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert records == [{"id": 2, "repository": "organization/repository", "updated_at": "2022-02-02T10:10:04Z"}]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:04Z"}}

    records = read_incremental(stream, stream_state)
    assert records == [
        {"id": 3, "repository": "organization/repository", "updated_at": "2022-02-02T10:10:06Z"},
        {"id": 4, "repository": "organization/repository", "updated_at": "2022-02-02T10:10:08Z"},
    ]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:08Z"}}


@responses.activate
def test_streams_read_full_refresh():

    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
    }

    repository_args_with_start_date = {**repository_args, "start_date": "2022-02-01T00:00:00Z"}

    def get_json_response(cursor_field):
        cursor_field = cursor_field or "updated_at"
        return [
            {"id": 1, cursor_field: "2022-02-01T00:00:00Z"},
            {"id": 2, cursor_field: "2022-02-02T00:00:00Z"},
        ]

    def get_records(cursor_field):
        cursor_field = cursor_field or "updated_at"
        return [
            {"id": 1, cursor_field: "2022-02-01T00:00:00Z", "repository": "organization/repository"},
            {"id": 2, cursor_field: "2022-02-02T00:00:00Z", "repository": "organization/repository"},
        ]

    for cls, url in [
        (Releases, "https://api.github.com/repos/organization/repository/releases"),
        (IssueEvents, "https://api.github.com/repos/organization/repository/issues/events"),
        (IssueMilestones, "https://api.github.com/repos/organization/repository/milestones"),
        (CommitComments, "https://api.github.com/repos/organization/repository/comments"),
        (Deployments, "https://api.github.com/repos/organization/repository/deployments"),
    ]:
        stream = cls(**repository_args_with_start_date)
        responses.add("GET", url, json=get_json_response(stream.cursor_field))
        records = read_full_refresh(stream)
        assert records == get_records(stream.cursor_field)[1:2]

    for cls, url in [
        (Tags, "https://api.github.com/repos/organization/repository/tags"),
        (IssueLabels, "https://api.github.com/repos/organization/repository/labels"),
        (Collaborators, "https://api.github.com/repos/organization/repository/collaborators"),
        (Branches, "https://api.github.com/repos/organization/repository/branches"),
    ]:
        stream = cls(**repository_args)
        responses.add("GET", url, json=get_json_response(stream.cursor_field))
        records = read_full_refresh(stream)
        assert records == get_records(stream.cursor_field)

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/stargazers",
        json=[
            {"starred_at": "2022-02-01T00:00:00Z", "user": {"id": 1}},
            {"starred_at": "2022-02-02T00:00:00Z", "user": {"id": 2}},
        ],
    )

    stream = Stargazers(**repository_args_with_start_date)
    records = read_full_refresh(stream)
    assert records == [{"repository": "organization/repository", "starred_at": "2022-02-02T00:00:00Z", "user": {"id": 2}, "user_id": 2}]


@responses.activate
def test_stream_reviews_incremental_read():

    url_pulls = "https://api.github.com/repos/organization/repository/pulls"

    repository_args_with_start_date = {
        "start_date": "2000-01-01T00:00:00Z",
        "page_size_for_large_streams": 30,
        "repositories": ["organization/repository"],
    }
    stream = Reviews(parent=PullRequests(**repository_args_with_start_date), **repository_args_with_start_date)

    responses.add(
        "GET",
        url_pulls,
        json=[
            {"updated_at": "2022-01-01T00:00:00Z", "number": 1},
            {"updated_at": "2022-01-02T00:00:00Z", "number": 2},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/1/reviews",
        json=[{"id": 1000, "body": "commit1"}, {"id": 1001, "body": "commit1"}],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/2/reviews",
        json=[{"id": 1002, "body": "commit1"}],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)

    assert records == [
        {"body": "commit1", "id": 1000, "pull_request_updated_at": "2022-01-01T00:00:00Z", "repository": "organization/repository"},
        {"body": "commit1", "id": 1001, "pull_request_updated_at": "2022-01-01T00:00:00Z", "repository": "organization/repository"},
        {"body": "commit1", "id": 1002, "pull_request_updated_at": "2022-01-02T00:00:00Z", "repository": "organization/repository"},
    ]

    assert stream_state == {"organization/repository": {"pull_request_updated_at": "2022-01-02T00:00:00Z"}}

    responses.add(
        "GET",
        url_pulls,
        json=[
            {"updated_at": "2022-01-03T00:00:00Z", "number": 1},
            {"updated_at": "2022-01-02T00:00:00Z", "number": 2},
            {"updated_at": "2022-01-04T00:00:00Z", "number": 3},
        ],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/1/reviews",
        json=[{"id": 1000, "body": "commit1"}, {"id": 1001, "body": "commit2"}],
    )

    responses.add(
        "GET",
        "https://api.github.com/repos/organization/repository/pulls/3/reviews",
        json=[{"id": 1003, "body": "commit1"}],
    )

    records = read_incremental(stream, stream_state)

    assert records == [
        {"body": "commit1", "id": 1000, "pull_request_updated_at": "2022-01-03T00:00:00Z", "repository": "organization/repository"},
        {"body": "commit2", "id": 1001, "pull_request_updated_at": "2022-01-03T00:00:00Z", "repository": "organization/repository"},
        {"body": "commit1", "id": 1003, "pull_request_updated_at": "2022-01-04T00:00:00Z", "repository": "organization/repository"},
    ]

    assert stream_state == {"organization/repository": {"pull_request_updated_at": "2022-01-04T00:00:00Z"}}

    assert len(responses.calls) == 6
    assert urlbase(responses.calls[0].request.url) == url_pulls
    # make sure parent stream PullRequests used ascending sorting for both HTTP requests
    assert responses.calls[0].request.params["direction"] == "asc"
    assert urlbase(responses.calls[3].request.url) == url_pulls
    assert responses.calls[3].request.params["direction"] == "asc"


@responses.activate
def test_stream_team_members_full_refresh():
    organization_args = {"organizations": ["org1"]}
    repository_args = {"repositories": [], "page_size_for_large_streams": 100}

    responses.add("GET", "https://api.github.com/orgs/org1/teams", json=[{"slug": "team1"}, {"slug": "team2"}])
    responses.add("GET", "https://api.github.com/orgs/org1/teams/team1/members", json=[{"login": "login1"}, {"login": "login2"}])
    responses.add("GET", "https://api.github.com/orgs/org1/teams/team1/memberships/login1", json={"username": "login1"})
    responses.add("GET", "https://api.github.com/orgs/org1/teams/team1/memberships/login2", json={"username": "login2"})
    responses.add("GET", "https://api.github.com/orgs/org1/teams/team2/members", json=[{"login": "login2"}])
    responses.add("GET", "https://api.github.com/orgs/org1/teams/team2/memberships/login2", json={"username": "login2"})

    stream = TeamMembers(parent=Teams(**organization_args), **repository_args)
    records = read_full_refresh(stream)

    assert records == [
        {"login": "login1", "organization": "org1", "team_slug": "team1"},
        {"login": "login2", "organization": "org1", "team_slug": "team1"},
        {"login": "login2", "organization": "org1", "team_slug": "team2"},
    ]

    stream = TeamMemberships(parent=stream, **repository_args)
    records = read_full_refresh(stream)

    assert records == [
        {"username": "login1", "organization": "org1", "team_slug": "team1"},
        {"username": "login2", "organization": "org1", "team_slug": "team1"},
        {"username": "login2", "organization": "org1", "team_slug": "team2"},
    ]

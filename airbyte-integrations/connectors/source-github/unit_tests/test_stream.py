#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import urllib
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
import responses
from attr.validators import matches_re
from responses import matchers
from source_github import SourceGithub, constants
from source_github.streams import (
    Branches,
    Collaborators,
    Comments,
    CommitCommentReactions,
    CommitComments,
    Commits,
    ContributorActivity,
    Deployments,
    GithubStreamABCBackoffStrategy,
    IssueEvents,
    IssueLabels,
    IssueMilestones,
    IssueTimelineEvents,
    Organizations,
    ProjectCards,
    ProjectColumns,
    Projects,
    ProjectsV2,
    PullRequestCommentReactions,
    PullRequestCommits,
    PullRequests,
    PullRequestStats,
    Releases,
    Repositories,
    RepositoryStats,
    Reviews,
    Stargazers,
    Tags,
    TeamMembers,
    TeamMemberships,
    Teams,
    Users,
    WorkflowJobs,
    WorkflowRuns,
)
from source_github.utils import read_full_refresh

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors
from airbyte_cdk.test.catalog_builder import CatalogBuilder

from .utils import ProjectsResponsesAPI, read_incremental


DEFAULT_BACKOFF_DELAYS = [1, 2, 4, 8, 16]


@patch("time.sleep")
def test_internal_server_error_retry(time_mock, requests_mock):
    args = {"authenticator": None, "repositories": ["airbytehq/airbyte"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = CommitCommentReactions(**args)
    stream_slice = {"repository": "airbytehq/airbyte", "comment_id": "id"}

    time_mock.reset_mock()
    requests_mock.get("https://api.github.com/repos/airbytehq/airbyte/comments/id/reactions", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    # http client raises MessageRepresentationAirbyteTracedErrors when BaseBackoffException occurs
    with pytest.raises(MessageRepresentationAirbyteTracedErrors):
        list(stream.read_records(sync_mode="full_refresh", stream_slice=stream_slice))

    sleep_delays = [delay[0][0] for delay in time_mock.call_args_list]
    assert sleep_delays == DEFAULT_BACKOFF_DELAYS


@pytest.mark.parametrize(
    ("http_status", "response_headers", "expected_backoff_time"),
    [
        (HTTPStatus.BAD_GATEWAY, {}, None),
        (HTTPStatus.INTERNAL_SERVER_ERROR, {}, None),
        (HTTPStatus.SERVICE_UNAVAILABLE, {}, None),
        (HTTPStatus.FORBIDDEN, {"Retry-After": "0"}, 60),
        (HTTPStatus.FORBIDDEN, {"Retry-After": "30"}, 60),
        (HTTPStatus.FORBIDDEN, {"Retry-After": "120"}, 120),
        (HTTPStatus.FORBIDDEN, {"X-RateLimit-Reset": "1655804454"}, 60.0),
        (HTTPStatus.FORBIDDEN, {"X-RateLimit-Reset": "1655804724"}, 300.0),
    ],
)
@patch("time.time", return_value=1655804424.0)
def test_backoff_time(time_mock, http_status, response_headers, expected_backoff_time):
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = http_status
    response_mock.headers = response_headers
    args = {"authenticator": None, "repositories": ["test_repo"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)
    assert stream.get_backoff_strategy().backoff_time(response_mock) == expected_backoff_time


@pytest.mark.parametrize(
    ("http_status", "response_headers", "text", "response_action", "error_message"),
    [
        (
            HTTPStatus.OK,
            {"X-RateLimit-Resource": "graphql"},
            '{"errors": [{"type": "RATE_LIMITED"}]}',
            ResponseAction.RATE_LIMITED,
            f"Response status code: {HTTPStatus.OK}. Retrying...",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"X-RateLimit-Remaining": "0"},
            "",
            ResponseAction.RATE_LIMITED,
            f"Response status code: {HTTPStatus.FORBIDDEN}. Retrying...",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"Retry-After": "0"},
            "",
            ResponseAction.RATE_LIMITED,
            f"Response status code: {HTTPStatus.FORBIDDEN}. Retrying...",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"Retry-After": "60"},
            "",
            ResponseAction.RATE_LIMITED,
            f"Response status code: {HTTPStatus.FORBIDDEN}. Retrying...",
        ),
        (HTTPStatus.INTERNAL_SERVER_ERROR, {}, "", ResponseAction.RETRY, "HTTP Status Code: 500. Error: Internal server error."),
        (HTTPStatus.BAD_GATEWAY, {}, "", ResponseAction.RETRY, "HTTP Status Code: 502. Error: Bad gateway."),
        (HTTPStatus.SERVICE_UNAVAILABLE, {}, "", ResponseAction.RETRY, "HTTP Status Code: 503. Error: Service unavailable."),
    ],
)
def test_error_handler(http_status, response_headers, text, response_action, error_message):
    stream = RepositoryStats(repositories=["test_repo"], page_size_for_large_streams=30)
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = http_status
    response_mock.headers = response_headers
    response_mock.text = text
    response_mock.ok = False
    response_mock.json = lambda: json.loads(text)

    expected = ErrorResolution(
        response_action=response_action,
        failure_type=FailureType.transient_error,
        error_message=error_message,  # type: ignore[union-attr]
    )
    assert stream.get_error_handler().interpret_response(response_mock) == expected


@patch("time.sleep")
def test_retry_after(time_mock, requests_mock):
    first_request = True

    def request_callback(request, context):
        nonlocal first_request
        if first_request:
            first_request = False
            context.status_code = HTTPStatus.FORBIDDEN
            context.headers = {}
            context.text = ""
            return ""
        context.status_code = HTTPStatus.OK
        context.headers = {}
        context.text = '{"login": "airbytehq"}'
        return '{"login": "airbytehq"}'

    requests_mock.get(
        "https://api.github.com/orgs/airbytehq",
        text=request_callback,
    )

    stream = Organizations(organizations=["airbytehq"])
    list(read_full_refresh(stream))
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/orgs/airbytehq?per_page=100"
    assert [r.url for r in requests_mock._adapter.request_history][1] == "https://api.github.com/orgs/airbytehq?per_page=100"


@patch("time.sleep")
@patch("time.time", return_value=1655804424.0)
def test_graphql_rate_limited(time_mock, sleep_mock, requests_mock):
    first_request = True

    def request_callback(request, context):
        nonlocal first_request
        if first_request:
            first_request = False
            context.status_code = HTTPStatus.OK
            context.headers = {"X-RateLimit-Limit": "5000", "X-RateLimit-Resource": "graphql", "X-RateLimit-Reset": "1655804724"}
            context.text = json.dumps({"errors": [{"type": "RATE_LIMITED"}]})

            return context.text

        context.status_code = HTTPStatus.OK
        context.headers = {"X-RateLimit-Limit": "5000", "X-RateLimit-Resource": "graphql", "X-RateLimit-Reset": "1655808324"}
        context.text = json.dumps({"data": {"repository": None}})

        return context.text

    requests_mock.post(
        "https://api.github.com/graphql",
        text=request_callback,
    )

    stream = PullRequestStats(repositories=["airbytehq/airbyte"], page_size_for_large_streams=30)
    records = list(read_full_refresh(stream))
    assert records == []
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/graphql"
    assert [r.url for r in requests_mock._adapter.request_history][1] == "https://api.github.com/graphql"
    assert sum([c[0][0] for c in sleep_mock.call_args_list]) > 300


@patch("time.sleep")
def test_stream_teams_404(time_mock, requests_mock):
    organization_args = {"organizations": ["org_name"]}
    stream = Teams(**organization_args)

    requests_mock.get(
        "https://api.github.com/orgs/org_name/teams",
        status_code=requests.codes.NOT_FOUND,
        json={"message": "Not Found", "documentation_url": "https://docs.github.com/rest/reference/teams#list-teams"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 6
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/orgs/org_name/teams?per_page=100"


@patch("time.sleep")
def test_stream_teams_502(sleep_mock, requests_mock):
    organization_args = {"organizations": ["org_name"]}
    stream = Teams(**organization_args)

    url = "https://api.github.com/orgs/org_name/teams"
    requests_mock.get(
        url=url,
        status_code=requests.codes.BAD_GATEWAY,
        json={"message": "Server Error"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 6
    # Check whether url is the same for all response.calls
    assert set(call.url for call in requests_mock._adapter.request_history).symmetric_difference({f"{url}?per_page=100"}) == set()


def test_stream_organizations_availability_report():
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Organizations(**organization_args)
    assert stream.availability_strategy is None


def test_stream_organizations_read(requests_mock):
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Organizations(**organization_args)
    requests_mock.get("https://api.github.com/orgs/org1", json={"id": 1})
    requests_mock.get("https://api.github.com/orgs/org2", json={"id": 2})
    records = list(read_full_refresh(stream))
    assert records == [{"id": 1}, {"id": 2}]


def test_stream_teams_read(requests_mock):
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Teams(**organization_args)
    stream._http_client._session.cache.clear()
    requests_mock.get("https://api.github.com/orgs/org1/teams", json=[{"id": 1}, {"id": 2}])
    requests_mock.get("https://api.github.com/orgs/org2/teams", json=[{"id": 3}])
    records = list(read_full_refresh(stream))
    assert records == [{"id": 1, "organization": "org1"}, {"id": 2, "organization": "org1"}, {"id": 3, "organization": "org2"}]
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/orgs/org1/teams?per_page=100"
    assert [r.url for r in requests_mock._adapter.request_history][1] == "https://api.github.com/orgs/org2/teams?per_page=100"


def test_stream_users_read(requests_mock):
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Users(**organization_args)
    requests_mock.get("https://api.github.com/orgs/org1/members", json=[{"id": 1}, {"id": 2}])
    requests_mock.get("https://api.github.com/orgs/org2/members", json=[{"id": 3}])
    records = list(read_full_refresh(stream))
    assert records == [{"id": 1, "organization": "org1"}, {"id": 2, "organization": "org1"}, {"id": 3, "organization": "org2"}]
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/orgs/org1/members?per_page=100"
    assert [r.url for r in requests_mock._adapter.request_history][1] == "https://api.github.com/orgs/org2/members?per_page=100"


@patch("time.sleep")
def test_stream_repositories_404(time_mock, requests_mock):
    organization_args = {"organizations": ["org_name"]}
    stream = Repositories(**organization_args)

    requests_mock.get(
        "https://api.github.com/orgs/org_name/repos",
        status_code=requests.codes.NOT_FOUND,
        json={"message": "Not Found", "documentation_url": "https://docs.github.com/rest/reference/repos#list-organization-repositories"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 6
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/orgs/org_name/repos?per_page=100&sort=updated&direction=desc"


@patch("time.sleep")
def test_stream_repositories_401(time_mock, caplog, requests_mock):
    organization_args = {"organizations": ["org_name"], "access_token_type": constants.PERSONAL_ACCESS_TOKEN_TITLE}
    stream = Repositories(**organization_args)

    requests_mock.get(
        "https://api.github.com/orgs/org_name/repos",
        status_code=requests.codes.UNAUTHORIZED,
        json={"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest"},
    )

    with pytest.raises(MessageRepresentationAirbyteTracedErrors):
        assert list(read_full_refresh(stream)) == []

    assert requests_mock.call_count == 6
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/orgs/org_name/repos?per_page=100&sort=updated&direction=desc"
    assert "Personal Access Token renewal is required: Bad credentials" in caplog.messages


@responses.activate
def test_stream_repositories_read(requests_mock):
    organization_args = {"organizations": ["org1", "org2"]}
    stream = Repositories(**organization_args)
    updated_at = "2020-01-01T00:00:00Z"
    requests_mock.get(
        "https://api.github.com/orgs/org1/repos", json=[{"id": 1, "updated_at": updated_at}, {"id": 2, "updated_at": updated_at}]
    )
    requests_mock.get("https://api.github.com/orgs/org2/repos", json=[{"id": 3, "updated_at": updated_at}])
    records = list(read_full_refresh(stream))
    assert records == [
        {"id": 1, "organization": "org1", "updated_at": updated_at},
        {"id": 2, "organization": "org1", "updated_at": updated_at},
        {"id": 3, "organization": "org2", "updated_at": updated_at},
    ]
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/orgs/org1/repos?per_page=100&sort=updated&direction=desc"
    assert [r.url for r in requests_mock._adapter.request_history][
        1
    ] == "https://api.github.com/orgs/org2/repos?per_page=100&sort=updated&direction=desc"


@patch("time.sleep")
def test_stream_projects_disabled(time_mock, requests_mock):
    repository_args_with_start_date = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["test_repo"]}

    stream = Projects(**repository_args_with_start_date)
    requests_mock.get(
        "https://api.github.com/repos/test_repo/projects",
        status_code=requests.codes.GONE,
        json={"message": "Projects are disabled for this repository", "documentation_url": "https://docs.github.com/v3/projects"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 6
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/repos/test_repo/projects?per_page=100&state=all"


def test_stream_pull_requests_incremental_read(requests_mock):
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

    requests_mock.get(
        f"{api_url}?per_page=2&state=all&sort=updated&direction=asc",
        json=data[0:2],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=2>; rel="next"'},
    )
    requests_mock.get(
        f"{api_url}?per_page=2&page=2&state=all&sort=updated&direction=asc",
        json=data[2:4],
    )
    requests_mock.get(
        f"{api_url}?per_page=2&state=all&sort=updated&direction=desc",
        json=data[5:3:-1],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=2>; rel="next"'},
    )
    requests_mock.get(
        f"{api_url}?per_page=2&page=2&state=all&sort=updated&direction=desc",
        json=data[3:1:-1],
        headers={"Link": '<https://api.github.com/repositories/400052213/pulls?page=3>; rel="next"'},
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [2, 3, 4]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:08Z"}}

    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [6, 5]
    assert stream_state == {"organization/repository": {"updated_at": "2022-02-02T10:10:12Z"}}


def test_stream_commits_incremental_read(requests_mock):
    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-02T10:10:03Z",
    }

    branches_to_pull = ["organization/repository/branch"]

    stream = Commits(**repository_args_with_start_date, branches_to_pull=branches_to_pull)
    stream.page_size = 2

    commits_data = [
        {"sha": 1, "commit": {"author": {"date": "2022-02-02T10:10:02Z"}}},
        {"sha": 2, "commit": {"author": {"date": "2022-02-02T10:10:04Z"}}},
        {"sha": 3, "commit": {"author": {"date": "2022-02-02T10:10:06Z"}}},
        {"sha": 4, "commit": {"author": {"date": "2022-02-02T10:10:08Z"}}},
        {"sha": 5, "commit": {"author": {"date": "2022-02-02T10:10:10Z"}}},
        {"sha": 6, "commit": {"author": {"date": "2022-02-02T10:10:12Z"}}},
        {"sha": 7, "commit": {"author": {"date": "2022-02-02T10:10:14Z"}}},
    ]

    repo_api_url = "https://api.github.com/repos/organization/repository"
    branches_api_url = "https://api.github.com/repos/organization/repository/branches"
    commits_api_url = "https://api.github.com/repos/organization/repository/commits"

    requests_mock.get(
        repo_api_url,
        json={"id": 1, "updated_at": "2022-02-02T10:10:02Z", "default_branch": "main", "full_name": "organization/repository"},
    )
    requests_mock.get(
        branches_api_url,
        json=[
            {
                "name": "branch",
                "commit": {
                    "sha": "74445338726f0f8e1c27c10dce90ca00c5ae2858",
                    "url": "https://api.github.com/repos/airbytehq/airbyte/commits/74445338726f0f8e1c27c10dce90ca00c5ae2858",
                },
                "protected": False,
            },
            {
                "name": "main",
                "commit": {
                    "sha": "c27c10dce90ca00c5ae285874445338726f0f8e1",
                    "url": "https://api.github.com/repos/airbytehq/airbyte/commits/c27c10dce90ca00c5ae285874445338726f0f8e1",
                },
                "protected": False,
            },
        ],
        status_code=200,
    )
    requests_mock.get(f"{commits_api_url}?per_page=2&since=2022-02-02T10%3A10%3A03Z&sha=branch", json=commits_data[0:3])

    requests_mock.get(
        f"{commits_api_url}?per_page=2&since=2022-02-02T10%3A10%3A06Z&sha=branch",
        json=commits_data[3:5],
        headers={"Link": '<https://api.github.com/repos/organization/repository/commits?page=2>; rel="next"'},
    )

    requests_mock.get(
        f"{commits_api_url}?per_page=2&page=2&since=2022-02-02T10%3A10%3A06Z&sha=branch",
        json=commits_data[5:7],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert [r["sha"] for r in records] == [2, 3]
    assert stream_state == {"organization/repository": {"branch": {"created_at": "2022-02-02T10:10:06Z"}}}
    records = read_incremental(stream, stream_state)
    assert [r["sha"] for r in records] == [4, 5, 6, 7]
    assert stream_state == {"organization/repository": {"branch": {"created_at": "2022-02-02T10:10:14Z"}}}


def test_stream_commits_409_empty_repository(caplog, requests_mock):
    """
    Adding tests for the case when the repository is empty and the API returns a 409 status code.
    We expect the specific error message in response 'Git Repository is empty.'
    """
    repository_args_with_start_date = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-02-02T10:10:03Z",
    }

    branches_to_pull = ["organization/repository/branch"]

    stream = Commits(**repository_args_with_start_date, branches_to_pull=branches_to_pull)
    stream.page_size = 2

    repo_api_url = "https://api.github.com/repos/organization/repository"
    branches_api_url = "https://api.github.com/repos/organization/repository/branches"
    commits_api_url = "https://api.github.com/repos/organization/repository/commits"

    requests_mock.get(
        repo_api_url,
        json={"id": 1, "updated_at": "2022-02-02T10:10:02Z", "default_branch": "main", "full_name": "organization/repository"},
    )
    requests_mock.get(
        branches_api_url,
        json=[
            {
                "name": "branch",
                "commit": {
                    "sha": "74445338726f0f8e1c27c10dce90ca00c5ae2858",
                    "url": "https://api.github.com/repos/airbytehq/airbyte/commits/74445338726f0f8e1c27c10dce90ca00c5ae2858",
                },
                "protected": False,
            }
        ],
        status_code=200,
    )
    empty_repository_message = {
        "message": "Git Repository is empty.",
        "documentation_url": "https://docs.github.com/rest/commits/commits#list-commits",
        "status": "409",
    }
    requests_mock.get(
        f"{commits_api_url}?per_page=2&since=2022-02-02T10%3A10%3A03Z&sha=branch",
        json=empty_repository_message,
        status_code=requests.codes.CONFLICT,
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert records == []
    ignore_message = "Ignoring response for 'GET' request to 'https://api.github.com/repos/organization/repository/commits?per_page=2&since=2022-02-02T10%3A10%3A03Z&sha=branch' with response code '409' as the repository is empty."
    assert ignore_message in caplog.messages


def test_stream_pull_request_commits(requests_mock):
    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
    }
    repository_args_with_start_date = {**repository_args, "start_date": "2022-02-02T10:10:02Z"}

    stream = PullRequestCommits(PullRequests(**repository_args_with_start_date), **repository_args)

    requests_mock.get(
        "https://api.github.com/repos/organization/repository/pulls",
        json=[
            {"id": 1, "updated_at": "2022-02-02T10:10:02Z", "number": 1},
            {"id": 2, "updated_at": "2022-02-02T10:10:04Z", "number": 2},
            {"id": 3, "updated_at": "2022-02-02T10:10:06Z", "number": 3},
        ],
    )

    requests_mock.get(
        "https://api.github.com/repos/organization/repository/pulls/2/commits",
        json=[{"sha": 1}, {"sha": 2}],
    )

    requests_mock.get(
        "https://api.github.com/repos/organization/repository/pulls/3/commits",
        json=[{"sha": 3}, {"sha": 4}],
    )

    records = list(read_full_refresh(stream))
    assert records == [
        {"sha": 1, "repository": "organization/repository", "pull_number": 2},
        {"sha": 2, "repository": "organization/repository", "pull_number": 2},
        {"sha": 3, "repository": "organization/repository", "pull_number": 3},
        {"sha": 4, "repository": "organization/repository", "pull_number": 3},
    ]


def test_stream_project_columns(requests_mock):
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

    ProjectsResponsesAPI.register(data, requests_mock)

    projects_stream = Projects(**repository_args_with_start_date)
    stream = ProjectColumns(projects_stream, **repository_args_with_start_date)
    projects_stream._http_client._session.cache.clear()
    stream._http_client._session.cache.clear()
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

    ProjectsResponsesAPI.register(data, requests_mock)

    projects_stream._http_client._session.cache.clear()
    stream._http_client._session.cache.clear()
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


def test_stream_project_cards(requests_mock):
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

    ProjectsResponsesAPI.register(data, requests_mock)

    stream_state = {}

    projects_stream._http_client._session.cache.clear()
    project_columns_stream._http_client._session.cache.clear()
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


def test_stream_comments(requests_mock):
    repository_args_with_start_date = {
        "repositories": ["organization/repository", "airbytehq/airbyte"],
        "page_size_for_large_streams": 2,
        "start_date": "2022-02-02T10:10:01Z",
    }

    stream = Comments(**repository_args_with_start_date)

    data = [
        {"id": 1, "updated_at": "2022-02-02T10:10:02Z"},
        {"id": 2, "updated_at": "2022-02-02T10:10:04Z"},
        {"id": 3, "updated_at": "2022-02-02T10:12:06Z"},
        {"id": 4, "updated_at": "2022-02-02T10:12:08Z"},
        {"id": 5, "updated_at": "2022-02-02T10:12:10Z"},
        {"id": 6, "updated_at": "2022-02-02T10:12:12Z"},
    ]

    api_url = "https://api.github.com/repos/organization/repository/issues/comments"

    requests_mock.get(f"{api_url}?per_page=2&since=2022-02-02T10:10:01Z", json=data[0:2])

    requests_mock.get(
        f"{api_url}?per_page=2&since=2022-02-02T10:10:04Z",
        json=data[1:3],
        headers={
            "Link": '<https://api.github.com/repos/organization/repository/issues/comments?per_page=2&since=2022-02-02T10%3A10%3A04Z&page=2>; rel="next"'
        },
    )

    requests_mock.get(
        f"{api_url}?per_page=2&page=2&since=2022-02-02T10:10:04Z",
        json=data[3:5],
        headers={
            "Link": '<https://api.github.com/repos/organization/repository/issues/comments?per_page=2&since=2022-02-02T10%3A10%3A04Z&page=3>; rel="next"'
        },
    )

    requests_mock.get(f"{api_url}?per_page=2&page=3&since=2022-02-02T10:10:04Z", json=data[5:])

    data = [
        {"id": 1, "updated_at": "2022-02-02T10:11:02Z"},
        {"id": 2, "updated_at": "2022-02-02T10:11:04Z"},
        {"id": 3, "updated_at": "2022-02-02T10:13:06Z"},
        {"id": 4, "updated_at": "2022-02-02T10:13:08Z"},
        {"id": 5, "updated_at": "2022-02-02T10:13:10Z"},
        {"id": 6, "updated_at": "2022-02-02T10:13:12Z"},
    ]

    api_url = "https://api.github.com/repos/airbytehq/airbyte/issues/comments"

    requests_mock.get(f"{api_url}?per_page=2&since=2022-02-02T10:10:01Z", json=data[0:2])

    requests_mock.get(
        f"{api_url}?per_page=2&since=2022-02-02T10:11:04Z",
        json=data[1:3],
        headers={
            "Link": '<https://api.github.com/repos/airbytehq/airbyte/issues/comments?per_page=2&since=2022-02-02T10%3A11%3A04Z&page=2>; rel="next"'
        },
    )

    requests_mock.get(
        f"{api_url}?per_page=2&page=2&since=2022-02-02T10:11:04Z",
        json=data[3:5],
        headers={
            "Link": '<https://api.github.com/repos/airbytehq/airbyte/issues/comments?per_page=2&since=2022-02-02T10%3A11%3A04Z&page=3>; rel="next"'
        },
    )

    requests_mock.get(
        f"{api_url}?per_page=2&page=3&since=2022-02-02T10:11:04Z",
        json=data[5:],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert records == [
        {"id": 1, "repository": "organization/repository", "updated_at": "2022-02-02T10:10:02Z"},
        {"id": 2, "repository": "organization/repository", "updated_at": "2022-02-02T10:10:04Z"},
        {"id": 1, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:11:02Z"},
        {"id": 2, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:11:04Z"},
    ]

    assert stream_state == {
        "airbytehq/airbyte": {"updated_at": "2022-02-02T10:11:04Z"},
        "organization/repository": {"updated_at": "2022-02-02T10:10:04Z"},
    }

    records = read_incremental(stream, stream_state)
    assert records == [
        {"id": 3, "repository": "organization/repository", "updated_at": "2022-02-02T10:12:06Z"},
        {"id": 4, "repository": "organization/repository", "updated_at": "2022-02-02T10:12:08Z"},
        {"id": 5, "repository": "organization/repository", "updated_at": "2022-02-02T10:12:10Z"},
        {"id": 6, "repository": "organization/repository", "updated_at": "2022-02-02T10:12:12Z"},
        {"id": 3, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:13:06Z"},
        {"id": 4, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:13:08Z"},
        {"id": 5, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:13:10Z"},
        {"id": 6, "repository": "airbytehq/airbyte", "updated_at": "2022-02-02T10:13:12Z"},
    ]
    assert stream_state == {
        "airbytehq/airbyte": {"updated_at": "2022-02-02T10:13:12Z"},
        "organization/repository": {"updated_at": "2022-02-02T10:12:12Z"},
    }


def test_streams_read_full_refresh(requests_mock):
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
        requests_mock.get(url, json=get_json_response(stream.cursor_field))
        records = list(read_full_refresh(stream))
        assert records == get_records(stream.cursor_field)[1:2]

    for cls, url in [
        (Tags, "https://api.github.com/repos/organization/repository/tags"),
        (IssueLabels, "https://api.github.com/repos/organization/repository/labels"),
        (Collaborators, "https://api.github.com/repos/organization/repository/collaborators"),
        (Branches, "https://api.github.com/repos/organization/repository/branches"),
    ]:
        stream = cls(**repository_args)
        requests_mock.get(url, json=get_json_response(stream.cursor_field))
        records = list(read_full_refresh(stream))
        assert records == get_records(stream.cursor_field)

    requests_mock.get(
        "https://api.github.com/repos/organization/repository/stargazers",
        json=[
            {"starred_at": "2022-02-01T00:00:00Z", "user": {"id": 1}},
            {"starred_at": "2022-02-02T00:00:00Z", "user": {"id": 2}},
        ],
    )

    stream = Stargazers(**repository_args_with_start_date)
    records = list(read_full_refresh(stream))
    assert records == [{"repository": "organization/repository", "starred_at": "2022-02-02T00:00:00Z", "user": {"id": 2}, "user_id": 2}]


def test_stream_reviews_incremental_read(requests_mock):
    repository_args_with_start_date = {
        "start_date": "2000-01-01T00:00:00Z",
        "page_size_for_large_streams": 30,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = Reviews(**repository_args_with_start_date)
    stream.page_size = 2

    f = Path(__file__).parent / "responses/graphql_reviews_responses.json"
    response_objects = json.load(open(f))

    def request_callback(request, context):
        context.status_code = 200
        context.headers = {"Content-Type": "application/json"}
        return json.dumps(response_objects.pop(0))

    requests_mock.post(
        "https://api.github.com/graphql",
        text=request_callback,
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]
    assert stream_state == {"airbytehq/airbyte": {"updated_at": "2000-01-01T00:00:01Z"}}
    assert requests_mock.call_count == 4

    requests_mock.reset_mock()
    records = read_incremental(stream, stream_state)
    assert [r["id"] for r in records] == [1000, 1007, 1009]
    assert stream_state == {"airbytehq/airbyte": {"updated_at": "2000-01-01T00:00:02Z"}}
    assert requests_mock.call_count == 4


@patch("time.sleep")
def test_stream_team_members_full_refresh(time_mock, caplog, rate_limit_mock_response, requests_mock):
    organization_args = {"organizations": ["org1"]}
    repository_args = {"repositories": [], "page_size_for_large_streams": 100}

    requests_mock.get("https://api.github.com/orgs/org1/teams", json=[{"slug": "team1"}, {"slug": "team2"}])
    requests_mock.get("https://api.github.com/orgs/org1/teams/team1/members", json=[{"login": "login1"}, {"login": "login2"}])
    requests_mock.get("https://api.github.com/orgs/org1/teams/team1/memberships/login1", json={"username": "login1"})
    requests_mock.get("https://api.github.com/orgs/org1/teams/team1/memberships/login2", json={"username": "login2"})
    requests_mock.get("https://api.github.com/orgs/org1/teams/team2/members", json=[{"login": "login2"}, {"login": "login3"}])
    requests_mock.get("https://api.github.com/orgs/org1/teams/team2/memberships/login2", json={"username": "login2"})
    requests_mock.get("https://api.github.com/orgs/org1/teams/team2/memberships/login3", status_code=requests.codes.NOT_FOUND)

    teams_stream = Teams(**organization_args)
    stream = TeamMembers(parent=teams_stream, **repository_args)
    teams_stream._http_client._session.cache.clear()
    records = list(read_full_refresh(stream))

    assert records == [
        {"login": "login1", "organization": "org1", "team_slug": "team1"},
        {"login": "login2", "organization": "org1", "team_slug": "team1"},
        {"login": "login2", "organization": "org1", "team_slug": "team2"},
        {"login": "login3", "organization": "org1", "team_slug": "team2"},
    ]

    stream = TeamMemberships(parent=stream, **repository_args)
    records = list(read_full_refresh(stream))

    assert records == [
        {"username": "login1", "organization": "org1", "team_slug": "team1"},
        {"username": "login2", "organization": "org1", "team_slug": "team1"},
        {"username": "login2", "organization": "org1", "team_slug": "team2"},
    ]
    expected_message = "Syncing `TeamMemberships` stream for organization `org1`, team `team2` and user `login3` isn't available: User has no team membership. Skipping..."
    assert expected_message in caplog.messages


def test_stream_commit_comment_reactions_incremental_read(requests_mock):
    repository_args = {"repositories": ["airbytehq/integration-test"], "page_size_for_large_streams": 100}
    stream = CommitCommentReactions(**repository_args)
    stream._parent_stream._http_client._session.cache.clear()

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments",
        json=[
            {"id": 55538825, "updated_at": "2021-01-01T15:00:00Z"},
            {"id": 55538826, "updated_at": "2021-01-01T16:00:00Z"},
        ],
    )

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments/55538825/reactions",
        json=[
            {"id": 154935429, "created_at": "2022-01-01T15:00:00Z"},
            {"id": 154935430, "created_at": "2022-01-01T16:00:00Z"},
        ],
    )

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments/55538826/reactions",
        json=[{"id": 154935431, "created_at": "2022-01-01T17:00:00Z"}],
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)

    assert stream_state == {
        "airbytehq/integration-test": {
            "55538825": {"created_at": "2022-01-01T16:00:00Z"},
            "55538826": {"created_at": "2022-01-01T17:00:00Z"},
        }
    }

    assert records == [
        {"id": 154935429, "comment_id": 55538825, "created_at": "2022-01-01T15:00:00Z", "repository": "airbytehq/integration-test"},
        {"id": 154935430, "comment_id": 55538825, "created_at": "2022-01-01T16:00:00Z", "repository": "airbytehq/integration-test"},
        {"id": 154935431, "comment_id": 55538826, "created_at": "2022-01-01T17:00:00Z", "repository": "airbytehq/integration-test"},
    ]

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments",
        json=[
            {"id": 55538825, "updated_at": "2021-01-01T15:00:00Z"},
            {"id": 55538826, "updated_at": "2021-01-01T16:00:00Z"},
            {"id": 55538827, "updated_at": "2022-02-01T15:00:00Z"},
        ],
    )

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments/55538826/reactions",
        json=[
            {"id": 154935431, "created_at": "2022-01-01T17:00:00Z"},
            {"id": 154935432, "created_at": "2022-02-01T16:00:00Z"},
        ],
    )

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/integration-test/comments/55538827/reactions",
        json=[{"id": 154935433, "created_at": "2022-02-01T17:00:00Z"}],
    )

    stream._parent_stream._http_client._session.cache.clear()
    records = read_incremental(stream, stream_state)

    assert records == [
        {"id": 154935432, "comment_id": 55538826, "created_at": "2022-02-01T16:00:00Z", "repository": "airbytehq/integration-test"},
        {"id": 154935433, "comment_id": 55538827, "created_at": "2022-02-01T17:00:00Z", "repository": "airbytehq/integration-test"},
    ]


def test_stream_workflow_runs_read_incremental(monkeypatch, requests_mock):
    repository_args_with_start_date = {
        "repositories": ["org/repos"],
        "page_size_for_large_streams": 30,
        "start_date": "2022-01-01T00:00:00Z",
    }

    monkeypatch.setattr(constants, "DEFAULT_PAGE_SIZE", 1)
    stream = WorkflowRuns(**repository_args_with_start_date)

    data = [
        {"id": 4, "created_at": "2022-02-05T00:00:00Z", "updated_at": "2022-02-05T00:00:00Z", "repository": {"full_name": "org/repos"}},
        {"id": 3, "created_at": "2022-01-15T00:00:00Z", "updated_at": "2022-01-15T00:00:00Z", "repository": {"full_name": "org/repos"}},
        {"id": 2, "created_at": "2022-01-03T00:00:00Z", "updated_at": "2022-01-03T00:00:00Z", "repository": {"full_name": "org/repos"}},
        {"id": 1, "created_at": "2022-01-02T00:00:00Z", "updated_at": "2022-01-02T00:00:00Z", "repository": {"full_name": "org/repos"}},
    ]

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1",
        json={"total_count": len(data), "workflow_runs": data[0:1]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=2>; rel="next"'},
    )
    #
    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=2",
        json={"total_count": len(data), "workflow_runs": data[1:2]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=3>; rel="next"'},
    )

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=3",
        json={"total_count": len(data), "workflow_runs": data[2:3]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=4>; rel="next"'},
    )

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=4",
        json={"total_count": len(data), "workflow_runs": data[3:4]},
    )

    state = {}
    records = read_incremental(stream, state)
    assert state == {"org/repos": {"updated_at": "2022-02-05T00:00:00Z"}}

    assert records == [
        {"id": 4, "repository": {"full_name": "org/repos"}, "created_at": "2022-02-05T00:00:00Z", "updated_at": "2022-02-05T00:00:00Z"},
        {"id": 3, "repository": {"full_name": "org/repos"}, "created_at": "2022-01-15T00:00:00Z", "updated_at": "2022-01-15T00:00:00Z"},
        {"id": 2, "repository": {"full_name": "org/repos"}, "created_at": "2022-01-03T00:00:00Z", "updated_at": "2022-01-03T00:00:00Z"},
        {"id": 1, "repository": {"full_name": "org/repos"}, "created_at": "2022-01-02T00:00:00Z", "updated_at": "2022-01-02T00:00:00Z"},
    ]

    assert requests_mock.call_count == 4

    data.insert(
        0,
        {
            "id": 5,
            "created_at": "2022-02-07T00:00:00Z",
            "updated_at": "2022-02-07T00:00:00Z",
            "repository": {"full_name": "org/repos"},
        },
    )

    data[2]["updated_at"] = "2022-02-08T00:00:00Z"

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1",
        json={"total_count": len(data), "workflow_runs": data[0:1]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=2>; rel="next"'},
    )

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=2",
        json={"total_count": len(data), "workflow_runs": data[1:2]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=3>; rel="next"'},
    )

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=3",
        json={"total_count": len(data), "workflow_runs": data[2:3]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=4>; rel="next"'},
    )

    requests_mock.get(
        "https://api.github.com/repos/org/repos/actions/runs?per_page=1&page=4",
        json={"total_count": len(data), "workflow_runs": data[3:4]},
        headers={"Link": '<https://api.github.com/repositories/283046497/actions/runs?per_page=1&page=5>; rel="next"'},
    )

    requests_mock.reset_mock()
    records = read_incremental(stream, state)

    assert state == {"org/repos": {"updated_at": "2022-02-08T00:00:00Z"}}
    assert records == [
        {"id": 5, "repository": {"full_name": "org/repos"}, "created_at": "2022-02-07T00:00:00Z", "updated_at": "2022-02-07T00:00:00Z"},
        {"id": 3, "repository": {"full_name": "org/repos"}, "created_at": "2022-01-15T00:00:00Z", "updated_at": "2022-02-08T00:00:00Z"},
    ]

    assert requests_mock.call_count == 4


def test_stream_workflow_jobs_read(requests_mock):
    repository_args = {
        "repositories": ["org/repo"],
        "page_size_for_large_streams": 100,
    }
    repository_args_with_start_date = {**repository_args, "start_date": "2022-09-02T09:05:00Z"}

    workflow_runs_stream = WorkflowRuns(**repository_args_with_start_date)
    stream = WorkflowJobs(workflow_runs_stream, **repository_args_with_start_date)

    workflow_runs = [
        {
            "id": 1,
            "created_at": "2022-09-02T09:00:00Z",
            "updated_at": "2022-09-02T09:10:02Z",
            "repository": {"full_name": "org/repo"},
        },
        {
            "id": 2,
            "created_at": "2022-09-02T09:06:00Z",
            "updated_at": "2022-09-02T09:08:00Z",
            "repository": {"full_name": "org/repo"},
        },
    ]

    workflow_jobs_1 = [
        {"id": 1, "completed_at": "2022-09-02T09:02:00Z", "run_id": 1},
        {"id": 4, "completed_at": "2022-09-02T09:10:00Z", "run_id": 1},
        {"id": 5, "completed_at": None, "run_id": 1},
    ]

    workflow_jobs_2 = [
        {"id": 2, "completed_at": "2022-09-02T09:07:00Z", "run_id": 2},
        {"id": 3, "completed_at": "2022-09-02T09:08:00Z", "run_id": 2},
    ]

    requests_mock.get(
        "https://api.github.com/repos/org/repo/actions/runs",
        json={"total_count": len(workflow_runs), "workflow_runs": workflow_runs},
    )
    requests_mock.get("https://api.github.com/repos/org/repo/actions/runs/1/jobs", json={"jobs": workflow_jobs_1})
    requests_mock.get("https://api.github.com/repos/org/repo/actions/runs/2/jobs", json={"jobs": workflow_jobs_2})

    state = {}
    records = read_incremental(stream, state)
    assert state == {"org/repo": {"completed_at": "2022-09-02T09:10:00Z"}}

    assert records == [
        {"completed_at": "2022-09-02T09:10:00Z", "id": 4, "repository": "org/repo", "run_id": 1},
        {"completed_at": "2022-09-02T09:07:00Z", "id": 2, "repository": "org/repo", "run_id": 2},
        {"completed_at": "2022-09-02T09:08:00Z", "id": 3, "repository": "org/repo", "run_id": 2},
    ]

    assert requests_mock.call_count == 3

    workflow_jobs_1[2]["completed_at"] = "2022-09-02T09:12:00Z"
    workflow_runs[0]["updated_at"] = "2022-09-02T09:12:01Z"
    workflow_runs.append(
        {
            "id": 3,
            "created_at": "2022-09-02T09:14:00Z",
            "updated_at": "2022-09-02T09:15:00Z",
            "repository": {"full_name": "org/repo"},
        }
    )
    workflow_jobs_3 = [
        {"id": 6, "completed_at": "2022-09-02T09:15:00Z", "run_id": 3},
        {"id": 7, "completed_at": None, "run_id": 3},
    ]

    requests_mock.get(
        "https://api.github.com/repos/org/repo/actions/runs",
        json={"total_count": len(workflow_runs), "workflow_runs": workflow_runs},
    )
    requests_mock.get("https://api.github.com/repos/org/repo/actions/runs/1/jobs", json={"jobs": workflow_jobs_1})
    requests_mock.get("https://api.github.com/repos/org/repo/actions/runs/2/jobs", json={"jobs": workflow_jobs_2})
    requests_mock.get("https://api.github.com/repos/org/repo/actions/runs/3/jobs", json={"jobs": workflow_jobs_3})

    requests_mock.reset_mock()
    records = read_incremental(stream, state)

    assert state == {"org/repo": {"completed_at": "2022-09-02T09:15:00Z"}}
    assert records == [
        {"completed_at": "2022-09-02T09:12:00Z", "id": 5, "repository": "org/repo", "run_id": 1},
        {"completed_at": "2022-09-02T09:15:00Z", "id": 6, "repository": "org/repo", "run_id": 3},
    ]

    records = list(read_full_refresh(stream))
    assert records == [
        {"id": 4, "completed_at": "2022-09-02T09:10:00Z", "run_id": 1, "repository": "org/repo"},
        {"id": 5, "completed_at": "2022-09-02T09:12:00Z", "run_id": 1, "repository": "org/repo"},
        {"id": 2, "completed_at": "2022-09-02T09:07:00Z", "run_id": 2, "repository": "org/repo"},
        {"id": 3, "completed_at": "2022-09-02T09:08:00Z", "run_id": 2, "repository": "org/repo"},
        {"id": 6, "completed_at": "2022-09-02T09:15:00Z", "run_id": 3, "repository": "org/repo"},
    ]


def test_stream_pull_request_comment_reactions_read(requests_mock):
    repository_args_with_start_date = {
        "start_date": "2022-01-01T00:00:00Z",
        "page_size_for_large_streams": 2,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = PullRequestCommentReactions(**repository_args_with_start_date)
    stream.page_size = 2

    f = Path(__file__).parent / "responses/pull_request_comment_reactions.json"
    response_objects = json.load(open(f))

    def request_callback(request, context):
        context.status_code = 200
        context.headers = {"Content-Type": "application/json"}
        return json.dumps(response_objects.pop(0))

    requests_mock.post(
        "https://api.github.com/graphql",
        text=request_callback,
    )

    stream_state = {}
    records = read_incremental(stream, stream_state)
    records = [{"comment_id": r["comment_id"], "created_at": r["created_at"], "node_id": r["node_id"]} for r in records]
    assert records == [
        {"comment_id": "comment1", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction1"},
        {"comment_id": "comment1", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction2"},
        {"comment_id": "comment2", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction3"},
        {"comment_id": "comment2", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction4"},
        {"comment_id": "comment2", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction5"},
        {"comment_id": "comment5", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction6"},
        {"comment_id": "comment7", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction7"},
        {"comment_id": "comment8", "created_at": "2022-01-01T00:00:01Z", "node_id": "reaction8"},
    ]

    assert stream_state == {"airbytehq/airbyte": {"created_at": "2022-01-01T00:00:01Z"}}
    records = read_incremental(stream, stream_state)
    records = [{"comment_id": r["comment_id"], "created_at": r["created_at"], "node_id": r["node_id"]} for r in records]

    assert records == [
        {"comment_id": "comment2", "created_at": "2022-01-02T00:00:01Z", "node_id": "reaction9"},
        {"comment_id": "comment8", "created_at": "2022-01-02T00:00:01Z", "node_id": "reaction10"},
    ]

    assert stream_state == {"airbytehq/airbyte": {"created_at": "2022-01-02T00:00:01Z"}}


@patch("time.sleep")
def test_stream_projects_v2_graphql_retry(time_mock, rate_limit_mock_response, requests_mock):
    repository_args_with_start_date = {
        "start_date": "2022-01-01T00:00:00Z",
        "page_size_for_large_streams": 20,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = ProjectsV2(**repository_args_with_start_date)
    resp = requests_mock.post("https://api.github.com/graphql", json={"errors": "not found"}, status_code=200, headers={"Retry-After": "5"})

    backoff_strategy = GithubStreamABCBackoffStrategy(stream)

    with patch.object(backoff_strategy, "backoff_time", return_value=0.01), pytest.raises(MessageRepresentationAirbyteTracedErrors):
        read_incremental(stream, stream_state={})
    assert requests_mock.call_count == stream.max_retries + 1


def test_stream_projects_v2_graphql_query(requests_mock):
    repository_args_with_start_date = {
        "start_date": "2022-01-01T00:00:00Z",
        "page_size_for_large_streams": 20,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = ProjectsV2(**repository_args_with_start_date)
    query = stream.request_body_json(stream_state={}, stream_slice={"repository": "airbytehq/airbyte"})
    requests_mock.post(
        "https://api.github.com/graphql",
        json=json.load(open(Path(__file__).parent / "responses/projects_v2_response.json")),
    )
    f = Path(__file__).parent / "projects_v2_pull_requests_query.json"
    expected_query = json.load(open(f))

    records = list(read_full_refresh(stream))
    assert query == expected_query
    assert records[0].get("owner_id")
    assert records[0].get("repository")


def test_stream_contributor_activity_parse_empty_response(caplog, requests_mock):
    repository_args = {
        "page_size_for_large_streams": 20,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = ContributorActivity(**repository_args)
    resp = requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/stats/contributors",
        body="",
        status_code=204,
    )
    records = list(read_full_refresh(stream))
    expected_message = "Empty response received for contributor_activity stats in repository airbytehq/airbyte"
    assert requests_mock.call_count == 1
    assert records == []
    assert expected_message in caplog.messages


def test_stream_contributor_activity_parse_empty_author(caplog, requests_mock):
    repository_args = {
        "page_size_for_large_streams": 20,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = ContributorActivity(**repository_args)
    contributions_without_author = [
        {
            "author": None,
            "total": 0,
            "weeks": [{"w": 1713052800, "a": 0, "d": 0, "c": 0}, {"w": 1713657600, "a": 0, "d": 0, "c": 0}],
            "repository": "airbytehq/airbyte",
        }
    ]
    response_body = json.dumps(contributions_without_author)
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/stats/contributors",
        text=response_body,
        status_code=200,
    )
    records = list(read_full_refresh(stream))
    # expected record should not contain author field as it is None
    del contributions_without_author[0]["author"]
    assert records == contributions_without_author


def test_stream_contributor_activity_accepted_response(caplog, rate_limit_mock_response, requests_mock):
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/test_airbyte?per_page=100",
        json={"full_name": "airbytehq/test_airbyte"},
        status_code=200,
    )
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/test_airbyte?per_page=100",
        json={"full_name": "airbytehq/test_airbyte", "default_branch": "default_branch"},
        status_code=200,
    )
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/test_airbyte/branches?per_page=100",
        json={},
        status_code=200,
    )
    resp = requests_mock.get(
        "https://api.github.com/repos/airbytehq/test_airbyte/stats/contributors?per_page=100",
        body="",
        status_code=202,
    )

    source = SourceGithub()
    catalog = CatalogBuilder().with_stream(name="contributor_activity", sync_mode=SyncMode.full_refresh).build()
    config = {"access_token": "test_token", "repository": "airbytehq/test_airbyte"}
    logger_mock = MagicMock()

    with patch("time.sleep", return_value=0):
        records = list(source.read(config=config, logger=logger_mock, catalog=catalog, state={}))

    assert records[2].log.message == "Syncing `ContributorActivity` stream isn't available for repository `airbytehq/test_airbyte`."
    assert resp.call_count == 6


def test_stream_contributor_activity_parse_response(requests_mock):
    repository_args = {
        "page_size_for_large_streams": 20,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = ContributorActivity(**repository_args)
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/airbyte/stats/contributors",
        json=json.load(open(Path(__file__).parent / "responses/contributor_activity_response.json")),
    )
    records = list(read_full_refresh(stream))
    assert len(records) == 1


def test_issues_timeline_events(requests_mock):
    repository_args = {
        "repositories": ["airbytehq/airbyte"],
        "page_size_for_large_streams": 20,
    }
    response_file = Path(__file__).parent / "responses/issue_timeline_events.json"
    response_json = json.load(open(response_file))
    requests_mock.get("https://api.github.com/repos/airbytehq/airbyte/issues/1/timeline?per_page=100", json=response_json)
    expected_file = Path(__file__).parent / "responses/issue_timeline_events_response.json"
    expected_records = json.load(open(expected_file))

    stream = IssueTimelineEvents(**repository_args)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"repository": "airbytehq/airbyte", "number": 1}))
    assert expected_records == records


def test_pull_request_stats(requests_mock):
    repository_args = {
        "page_size_for_large_streams": 10,
        "repositories": ["airbytehq/airbyte"],
    }
    stream = PullRequestStats(**repository_args)
    query = stream.request_body_json(stream_state={}, stream_slice={"repository": "airbytehq/airbyte"})
    requests_mock.post(
        "https://api.github.com/graphql",
        json=json.load(open(Path(__file__).parent / "responses/pull_request_stats_response.json")),
    )
    f = Path(__file__).parent / "pull_request_stats_query.json"
    expected_query = json.load(open(f))

    list(read_full_refresh(stream))
    assert query == expected_query

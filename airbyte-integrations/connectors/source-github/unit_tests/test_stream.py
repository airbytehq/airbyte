#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from source_github import constants
from source_github.errors_handlers import GitHubGraphQLErrorHandler, is_conflict_with_empty_repository, is_gone_with_feature_disabled
from source_github.streams import (
    GithubStreamABCBackoffStrategy,
    ProjectsV2,
    PullRequestCommentReactions,
    PullRequestStats,
    Releases,
    Reviews,
)
from source_github.utils import read_full_refresh

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .utils import ProbeStream, read_incremental


DEFAULT_BACKOFF_DELAYS = [1, 2, 4, 8, 16]


@patch("time.sleep")
def test_internal_server_error_retry(time_mock, requests_mock):
    args = {"authenticator": None, "repositories": ["airbytehq/airbyte"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = ProbeStream(**args)
    stream_slice = {"repository": "airbytehq/airbyte"}

    time_mock.reset_mock()
    requests_mock.get("https://api.github.com/repos/airbytehq/airbyte/probe_stream", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    # http client raises AirbyteTracedException when BaseBackoffException occurs
    with pytest.raises(AirbyteTracedException):
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
        (HTTPStatus.FORBIDDEN, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1655804454"}, 60.0),
        (HTTPStatus.FORBIDDEN, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1655804724"}, 300.0),
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


def test_non_rate_limited_404_does_not_wait_for_reset():
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.NOT_FOUND
    response_mock.headers = {"X-RateLimit-Reset": "1655808024"}
    args = {"authenticator": None, "repositories": ["test_repo"], "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)

    with patch("time.time", return_value=1655804424.0):
        assert stream.get_backoff_strategy().backoff_time(response_mock) is None


def test_retry_after_takes_precedence_over_reset():
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.FORBIDDEN
    response_mock.headers = {
        "Retry-After": "120",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1655808024",
    }
    args = {"authenticator": None, "repositories": ["test_repo"], "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)

    with patch("time.time", return_value=1655804424.0):
        assert stream.get_backoff_strategy().backoff_time(response_mock) == 120.0


def test_rate_limit_wait_is_bounded():
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.FORBIDDEN
    response_mock.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1655804724"}
    args = {
        "authenticator": None,
        "repositories": ["test_repo"],
        "start_date": "start_date",
        "page_size_for_large_streams": 30,
        "max_wait_time_seconds": 120,
    }
    stream = PullRequestCommentReactions(**args)

    with patch("time.time", return_value=1655804424.0):
        assert stream.get_backoff_strategy().backoff_time(response_mock) is None


def test_graphql_rate_limit_wait_applies():
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.OK
    response_mock.headers = {"X-RateLimit-Resource": "graphql", "X-RateLimit-Reset": "1655804724"}
    response_mock.json.return_value = {"errors": [{"type": "RATE_LIMITED"}]}
    args = {"authenticator": None, "repositories": ["test_repo"], "page_size_for_large_streams": 30}
    stream = ProjectsV2(**args)

    with patch("time.time", return_value=1655804424.0):
        assert stream.get_backoff_strategy().backoff_time(response_mock) == 300.0


@pytest.mark.parametrize(
    ("http_status", "response_headers", "text", "response_action", "error_message"),
    [
        (
            HTTPStatus.OK,
            {"X-RateLimit-Resource": "graphql"},
            '{"errors": [{"type": "RATE_LIMITED"}]}',
            ResponseAction.RATE_LIMITED,
            "GitHub rate limit hit for stream `probe_stream` (HTTP 200). Waiting for the rate limit window to reset before retrying.",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"X-RateLimit-Remaining": "0"},
            "",
            ResponseAction.RATE_LIMITED,
            "GitHub rate limit hit for stream `probe_stream` (HTTP 403). Waiting for the rate limit window to reset before retrying.",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"Retry-After": "0"},
            "",
            ResponseAction.RATE_LIMITED,
            "GitHub rate limit hit for stream `probe_stream` (HTTP 403). Waiting for the rate limit window to reset before retrying.",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"Retry-After": "60"},
            "",
            ResponseAction.RATE_LIMITED,
            "GitHub rate limit hit for stream `probe_stream` (HTTP 403). Waiting for the rate limit window to reset before retrying.",
        ),
        (HTTPStatus.INTERNAL_SERVER_ERROR, {}, "", ResponseAction.RETRY, "HTTP Status Code: 500. Error: Internal server error."),
        (HTTPStatus.BAD_GATEWAY, {}, "", ResponseAction.RETRY, "HTTP Status Code: 502. Error: Bad gateway."),
        (HTTPStatus.SERVICE_UNAVAILABLE, {}, "", ResponseAction.RETRY, "HTTP Status Code: 503. Error: Service unavailable."),
    ],
)
def test_error_handler(http_status, response_headers, text, response_action, error_message):
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
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


def test_permission_403_fails_immediately():
    """
    Verify that a 403 response without rate-limit headers (i.e. a genuine permission error)
    results in ResponseAction.FAIL rather than RETRY, preventing infinite retry loops.
    """
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.FORBIDDEN
    response_mock.headers = {}
    response_mock.text = '{"message": "Resource not accessible by personal access token"}'
    response_mock.ok = False
    response_mock.json = lambda: json.loads(response_mock.text)

    result = stream.get_error_handler().interpret_response(response_mock)
    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == FailureType.config_error
    assert "GitHub denied access (HTTP 403)" in result.error_message
    assert "SAML SSO authorization" in result.error_message


@pytest.mark.parametrize(
    ("response_headers",),
    [
        pytest.param({"X-RateLimit-Remaining": "0"}, id="rate_limit_remaining_zero"),
        pytest.param({"Retry-After": "30"}, id="retry_after_header"),
    ],
)
def test_rate_limit_403_retries(response_headers):
    """
    Verify that 403 responses WITH rate-limit headers are still handled as RATE_LIMITED
    (handled upstream by GithubStreamABCErrorHandler before the error mapping is reached).
    """
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = HTTPStatus.FORBIDDEN
    response_mock.headers = response_headers
    response_mock.text = ""
    response_mock.ok = False

    result = stream.get_error_handler().interpret_response(response_mock)
    assert result.response_action == ResponseAction.RATE_LIMITED
    assert result.failure_type == FailureType.transient_error


@pytest.mark.parametrize(
    "status_code,body,expected",
    [
        pytest.param(
            requests.codes.GONE,
            {"message": "Issues are disabled for this repo"},
            True,
            id="issues_disabled",
        ),
        pytest.param(
            requests.codes.GONE,
            {"message": "Projects are disabled for this repository"},
            True,
            id="projects_disabled",
        ),
        pytest.param(
            requests.codes.GONE,
            {"message": "Some other gone message"},
            False,
            id="unrelated_410_message",
        ),
        pytest.param(
            requests.codes.GONE,
            {},
            False,
            id="empty_body",
        ),
        pytest.param(
            requests.codes.NOT_FOUND,
            {"message": "Issues are disabled for this repo"},
            False,
            id="non_410_status",
        ),
        pytest.param(
            requests.codes.GONE,
            {"message": None},
            False,
            id="null_message",
        ),
    ],
)
def test_is_gone_with_feature_disabled(status_code, body, expected):
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = status_code
    response_mock.json = lambda: body
    assert is_gone_with_feature_disabled(response_mock) is expected


def test_error_handler_410_feature_disabled_returns_ignore():
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = requests.codes.GONE
    response_mock.headers = {}
    response_mock.text = '{"message": "Issues are disabled for this repo"}'
    response_mock.ok = False
    response_mock.json = lambda: json.loads(response_mock.text)
    response_mock.url = "https://api.github.com/repos/test_repo/issues"

    result = stream.get_error_handler().interpret_response(response_mock)
    assert result.response_action == ResponseAction.IGNORE
    assert result.failure_type == FailureType.config_error


def test_is_gone_with_feature_disabled_malformed_json():
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = requests.codes.GONE
    response_mock.json = MagicMock(side_effect=ValueError("not json"))
    assert is_gone_with_feature_disabled(response_mock) is False


def test_error_handler_410_unknown_body_returns_fail():
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    response_mock = MagicMock(spec=requests.Response)
    response_mock.status_code = requests.codes.GONE
    response_mock.headers = {}
    response_mock.text = '{"message": "Something else entirely"}'
    response_mock.ok = False
    response_mock.json = lambda: json.loads(response_mock.text)

    result = stream.get_error_handler().interpret_response(response_mock)
    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == FailureType.config_error


@patch("time.sleep")
def test_retry_after_rate_limit(time_mock, requests_mock):
    """
    A 403 with a Retry-After header is a rate-limit and should be retried.
    """
    first_request = True

    def request_callback(request, context):
        nonlocal first_request
        if first_request:
            first_request = False
            context.status_code = HTTPStatus.FORBIDDEN
            context.headers = {"Retry-After": "0"}
            context.text = ""
            return ""
        context.status_code = HTTPStatus.OK
        context.headers = {}
        context.text = '[{"id": 1}]'
        return '[{"id": 1}]'

    requests_mock.get(
        "https://api.github.com/repos/airbytehq/repo/probe_stream",
        text=request_callback,
    )

    stream = ProbeStream(repositories=["airbytehq/repo"], page_size_for_large_streams=10)
    list(read_full_refresh(stream))
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/repos/airbytehq/repo/probe_stream?per_page=100"
    assert [r.url for r in requests_mock._adapter.request_history][
        1
    ] == "https://api.github.com/repos/airbytehq/repo/probe_stream?per_page=100"


@patch("time.sleep")
def test_permission_403_raises_error(time_mock, requests_mock):
    """
    A bare 403 (no rate-limit headers) is a permission error and should fail immediately,
    not retry indefinitely.
    """
    requests_mock.get(
        "https://api.github.com/repos/airbytehq/repo/probe_stream",
        status_code=HTTPStatus.FORBIDDEN,
        json={"message": "Resource not accessible by personal access token"},
    )

    stream = ProbeStream(repositories=["airbytehq/repo"], page_size_for_large_streams=10)
    with pytest.raises((AirbyteTracedException, AttributeError)):
        list(read_full_refresh(stream))
    # Should fail on first attempt, not retry
    assert requests_mock.call_count == 1


@patch("time.sleep")
def test_read_records_404_message_for_repository_stream(time_mock, caplog, requests_mock):
    args = {"authenticator": None, "repositories": ["org/missing-repo"], "page_size_for_large_streams": 30}
    stream = ProbeStream(**args)

    requests_mock.get(
        "https://api.github.com/repos/org/missing-repo/probe_stream",
        status_code=requests.codes.NOT_FOUND,
        json={"message": "Not Found"},
    )

    list(read_full_refresh(stream))
    assert any(
        "Skipping `ProbeStream` for repository `org/missing-repo`" in msg and "GitHub returned 404 Not Found" in msg
        for msg in caplog.messages
    )


@patch("time.sleep")
def test_read_records_403_raises_with_actionable_message(time_mock, requests_mock):
    args = {"authenticator": None, "repositories": ["org/private-repo"], "page_size_for_large_streams": 30}
    stream = ProbeStream(**args)

    requests_mock.get(
        "https://api.github.com/repos/org/private-repo/probe_stream",
        status_code=requests.codes.FORBIDDEN,
        json={"message": "Resource not accessible by integration"},
    )

    with pytest.raises(AirbyteTracedException) as exc_info:
        list(read_full_refresh(stream))
    assert "GitHub denied access (HTTP 403)" in str(exc_info.value)
    assert "SAML SSO authorization" in str(exc_info.value)


@patch("time.sleep")
def test_read_records_409_conflict_message(time_mock, caplog, requests_mock):
    args = {"authenticator": None, "repositories": ["org/empty-repo"], "page_size_for_large_streams": 30}
    stream = ProbeStream(**args)

    requests_mock.get(
        "https://api.github.com/repos/org/empty-repo/probe_stream",
        status_code=requests.codes.CONFLICT,
        json={"message": "Git Repository is not empty but not a conflict either"},
    )

    list(read_full_refresh(stream))
    assert any(
        "Skipping `probe_stream` for repository `org/empty-repo`" in msg
        and "GitHub returned 409 Conflict" in msg
        and "empty (no commits)" in msg
        for msg in caplog.messages
    )


@patch("time.sleep")
def test_read_records_502_message(time_mock, caplog, requests_mock):
    args = {"authenticator": None, "repositories": ["org/repo"], "page_size_for_large_streams": 30}
    stream = ProbeStream(**args)

    requests_mock.get(
        "https://api.github.com/repos/org/repo/probe_stream",
        status_code=requests.codes.BAD_GATEWAY,
        json={"message": "Server Error"},
    )

    list(read_full_refresh(stream))
    assert any(
        "GitHub returned HTTP 502 Bad Gateway for stream `probe_stream`" in msg and "usually transient" in msg for msg in caplog.messages
    )


@patch("time.sleep")
def test_read_records_410_projects_disabled_message(time_mock, caplog, requests_mock):
    repository_args_with_start_date = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["org/repo"]}
    stream = ProbeStream(**repository_args_with_start_date)

    requests_mock.get(
        "https://api.github.com/repos/org/repo/probe_stream",
        status_code=requests.codes.GONE,
        json={"message": "Projects are disabled for this repository"},
    )

    list(read_full_refresh(stream))
    assert any("Projects are disabled for this repository" in msg for msg in caplog.messages)


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
    stream = ProbeStream(repositories=["org_name/repo"], page_size_for_large_streams=10)

    requests_mock.get(
        "https://api.github.com/repos/org_name/repo/probe_stream",
        status_code=requests.codes.NOT_FOUND,
        json={"message": "Not Found", "documentation_url": "https://docs.github.com/rest/reference/teams#list-teams"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 6
    assert [r.url for r in requests_mock._adapter.request_history][
        0
    ] == "https://api.github.com/repos/org_name/repo/probe_stream?per_page=100"


@patch("time.sleep")
def test_stream_teams_502(sleep_mock, requests_mock):
    stream = ProbeStream(repositories=["org_name/repo"], page_size_for_large_streams=10)

    url = "https://api.github.com/repos/org_name/repo/probe_stream"
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
    """The Python base still opts out of the availability strategy."""
    stream = ProbeStream(repositories=["org1/repo", "org2/repo"], page_size_for_large_streams=10)
    assert stream.availability_strategy is None


@patch("time.sleep")
def test_stream_401_logs_pat_renewal_hint(time_mock, caplog, requests_mock):
    """Replaces the deleted test_stream_repositories_401: GithubStreamABC.read_records still logs
    the PAT-renewal hint on 401 and re-raises, for every stream still on the Python path."""
    stream = ProbeStream(
        repositories=["org1/repo"], page_size_for_large_streams=10, access_token_type=constants.PERSONAL_ACCESS_TOKEN_TITLE
    )

    requests_mock.get(
        "https://api.github.com/repos/org1/repo/probe_stream",
        status_code=requests.codes.UNAUTHORIZED,
        json={"message": "Bad credentials", "documentation_url": "https://docs.github.com/rest"},
    )

    with pytest.raises(AirbyteTracedException):
        list(read_full_refresh(stream))

    # 1 initial attempt + GithubStreamABC.max_retries (5), matching GITHUB_DEFAULT_ERROR_MAPPING[401] = RETRY.
    assert requests_mock.call_count == 6
    assert any(
        "GitHub authentication failed (HTTP 401) for stream" in message and "Personal Access Token may need to be renewed" in message
        for message in caplog.messages
    )


def test_stream_read_stamps_the_repository(requests_mock):
    stream = ProbeStream(repositories=["org1/repo", "org2/repo"], page_size_for_large_streams=10)
    requests_mock.get("https://api.github.com/repos/org1/repo/probe_stream", json=[{"id": 1}, {"id": 2}])
    requests_mock.get("https://api.github.com/repos/org2/repo/probe_stream", json=[{"id": 3}])
    records = list(read_full_refresh(stream))
    assert records == [{"id": 1, "repository": "org1/repo"}, {"id": 2, "repository": "org1/repo"}, {"id": 3, "repository": "org2/repo"}]
    assert requests_mock.call_count == 2
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/repos/org1/repo/probe_stream?per_page=100"
    assert [r.url for r in requests_mock._adapter.request_history][1] == "https://api.github.com/repos/org2/repo/probe_stream?per_page=100"


def test_stream_projects_disabled(requests_mock):
    repository_args_with_start_date = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["test_repo"]}

    stream = ProbeStream(**repository_args_with_start_date)
    requests_mock.get(
        "https://api.github.com/repos/test_repo/probe_stream",
        status_code=requests.codes.GONE,
        json={"message": "Projects are disabled for this repository", "documentation_url": "https://docs.github.com/v3/projects"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 1
    assert [r.url for r in requests_mock._adapter.request_history][0] == "https://api.github.com/repos/test_repo/probe_stream?per_page=100"


def test_stream_feature_disabled(requests_mock):
    """A 410 naming a disabled feature is swallowed and the stream yields nothing.

    This pins `GithubStreamABCErrorHandler`/`is_gone_with_feature_disabled` on the Python side,
    which used to be exercised through `Issues` and then `Projects`; both are declarative now and
    their equivalent lives in `test_manifest_repo_scoped_streams.py`.
    """
    repository_args_with_start_date = {
        "start_date": "2022-01-01T00:00:00Z",
        "page_size_for_large_streams": 30,
        "repositories": ["test_repo"],
    }

    stream = ProbeStream(**repository_args_with_start_date)
    requests_mock.get(
        "https://api.github.com/repos/test_repo/probe_stream",
        status_code=requests.codes.GONE,
        json={"message": "Projects are disabled for this repo"},
    )

    assert list(read_full_refresh(stream)) == []
    assert requests_mock.call_count == 1


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

    graphql_releases_response = {
        "data": {
            "repository": {
                "name": "repository",
                "owner": {"login": "organization"},
                "releases": {
                    "nodes": [
                        {
                            "id": 1,
                            "node_id": "R_1",
                            "created_at": "2022-02-01T00:00:00Z",
                            "published_at": "2022-02-01T00:00:00Z",
                            "updated_at": "2022-02-01T00:00:00Z",
                            "name": "v1.0",
                            "tag_name": "v1.0",
                            "draft": False,
                            "prerelease": False,
                            "body": "",
                            "body_html": "",
                            "html_url": "https://github.com/organization/repository/releases/tag/v1.0",
                            "author": None,
                            "assets": {"nodes": [], "pageInfo": {"hasNextPage": False}},
                            "mentions_connection": {"totalCount": 0},
                            "tagCommit": {"target_commitish": "abc123"},
                            "reaction_groups": [],
                        },
                        {
                            "id": 2,
                            "node_id": "R_2",
                            "created_at": "2022-02-02T00:00:00Z",
                            "published_at": "2022-02-02T00:00:00Z",
                            "updated_at": "2022-02-02T00:00:00Z",
                            "name": "v2.0",
                            "tag_name": "v2.0",
                            "draft": False,
                            "prerelease": False,
                            "body": "",
                            "body_html": "",
                            "html_url": "https://github.com/organization/repository/releases/tag/v2.0",
                            "author": None,
                            "assets": {"nodes": [], "pageInfo": {"hasNextPage": False}},
                            "mentions_connection": {"totalCount": 0},
                            "tagCommit": {"target_commitish": "def456"},
                            "reaction_groups": [{"content": "THUMBS_UP", "reactors": {"totalCount": 1}}],
                        },
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    requests_mock.post("https://api.github.com/graphql", json=graphql_releases_response)
    stream = Releases(**repository_args_with_start_date)
    records = list(read_full_refresh(stream))
    assert len(records) == 1
    assert records[0]["id"] == 2
    assert records[0]["repository"] == "organization/repository"
    assert records[0]["url"] == "https://api.github.com/repos/organization/repository/releases/2"
    assert records[0]["assets_url"] == "https://api.github.com/repos/organization/repository/releases/2/assets"
    assert records[0]["tarball_url"] == "https://api.github.com/repos/organization/repository/tarball/v2.0"
    assert records[0]["zipball_url"] == "https://api.github.com/repos/organization/repository/zipball/v2.0"
    assert records[0]["reactions"] == {
        "plus_one": 1,
        "minus_one": 0,
        "laugh": 0,
        "hooray": 0,
        "confused": 0,
        "heart": 0,
        "rocket": 0,
        "eyes": 0,
        "total_count": 1,
    }

    # `assignees`, `branches`, `collaborators`, `issue_labels` and `tags` moved to the
    # manifest; their read behavior is covered by test_manifest_repo_scoped_streams.py.


def test_releases_draft_release_null_tag(requests_mock):
    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-01-01T00:00:00Z",
    }
    graphql_response = {
        "data": {
            "repository": {
                "name": "repository",
                "owner": {"login": "organization"},
                "releases": {
                    "nodes": [
                        {
                            "id": 10,
                            "node_id": "R_draft",
                            "created_at": "2022-03-01T00:00:00Z",
                            "published_at": None,
                            "updated_at": "2022-03-01T00:00:00Z",
                            "name": "Draft Release",
                            "tag_name": None,
                            "draft": True,
                            "prerelease": False,
                            "body": "WIP",
                            "body_html": "<p>WIP</p>",
                            "html_url": "https://github.com/organization/repository/releases/tag/untagged",
                            "author": {
                                "id": 1,
                                "login": "dev",
                                "avatar_url": "",
                                "html_url": "",
                                "site_admin": False,
                                "__typename": "User",
                            },
                            "assets": {"nodes": [], "pageInfo": {"hasNextPage": False}},
                            "mentions_connection": {"totalCount": 0},
                            "tagCommit": None,
                            "reaction_groups": [],
                        },
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    requests_mock.post("https://api.github.com/graphql", json=graphql_response)
    stream = Releases(**repository_args)
    records = list(read_full_refresh(stream))
    assert len(records) == 1
    record = records[0]
    assert record["tag_name"] is None
    assert record["draft"] is True
    assert record["target_commitish"] is None
    assert record["tarball_url"] is None
    assert record["zipball_url"] is None
    assert record["url"] == "https://api.github.com/repos/organization/repository/releases/10"
    assert record["assets_url"] == "https://api.github.com/repos/organization/repository/releases/10/assets"


def test_releases_asset_truncation_warning(requests_mock, caplog):
    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-01-01T00:00:00Z",
    }
    graphql_response = {
        "data": {
            "repository": {
                "name": "repository",
                "owner": {"login": "organization"},
                "releases": {
                    "nodes": [
                        {
                            "id": 20,
                            "node_id": "R_many_assets",
                            "created_at": "2022-04-01T00:00:00Z",
                            "published_at": "2022-04-01T00:00:00Z",
                            "updated_at": "2022-04-01T00:00:00Z",
                            "name": "v3.0",
                            "tag_name": "v3.0",
                            "draft": False,
                            "prerelease": False,
                            "body": "",
                            "body_html": "",
                            "html_url": "https://github.com/organization/repository/releases/tag/v3.0",
                            "author": None,
                            "assets": {
                                "nodes": [
                                    {
                                        "node_id": f"A_{i}",
                                        "name": f"asset_{i}.zip",
                                        "content_type": "application/zip",
                                        "size": 1024,
                                        "download_count": 0,
                                        "created_at": "2022-04-01T00:00:00Z",
                                        "updated_at": "2022-04-01T00:00:00Z",
                                        "browser_download_url": f"https://example.com/asset_{i}.zip",
                                        "url": f"https://api.github.com/repos/organization/repository/releases/assets/{i}",
                                        "uploader": {"id": 1},
                                    }
                                    for i in range(100)
                                ],
                                "pageInfo": {"hasNextPage": True},
                            },
                            "mentions_connection": {"totalCount": 0},
                            "tagCommit": {"target_commitish": "abc"},
                            "reaction_groups": [],
                        },
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    requests_mock.post("https://api.github.com/graphql", json=graphql_response)
    stream = Releases(**repository_args)
    records = list(read_full_refresh(stream))
    assert len(records) == 1
    assert len(records[0]["assets"]) == 100
    assert any(">100 assets" in msg for msg in caplog.messages)


@pytest.mark.parametrize(
    "node_id,expected_id",
    [
        pytest.param("RA_kwDODKw3uc4Vg-A4", 360964152, id="valid_release_asset_node_id"),
        pytest.param("RA_kwDODKw3uc4Vg-A6", 360964154, id="valid_release_asset_node_id_2"),
        pytest.param(None, None, id="none_node_id"),
        pytest.param("", None, id="empty_string"),
        pytest.param("no_underscore_prefix", None, id="malformed_no_prefix"),
    ],
)
def test_releases_extract_database_id_from_node_id(node_id, expected_id):
    assert Releases._extract_database_id_from_node_id(node_id) == expected_id


def test_releases_pagination(requests_mock):
    repository_args = {
        "repositories": ["organization/repository"],
        "page_size_for_large_streams": 100,
        "start_date": "2022-01-01T00:00:00Z",
    }

    def make_release(release_id, tag, date):
        return {
            "id": release_id,
            "node_id": f"R_{release_id}",
            "created_at": date,
            "published_at": date,
            "updated_at": date,
            "name": tag,
            "tag_name": tag,
            "draft": False,
            "prerelease": False,
            "body": "",
            "body_html": "",
            "html_url": f"https://github.com/organization/repository/releases/tag/{tag}",
            "author": None,
            "assets": {"nodes": [], "pageInfo": {"hasNextPage": False}},
            "mentions_connection": {"totalCount": 0},
            "tagCommit": {"target_commitish": "abc"},
            "reaction_groups": [],
        }

    page1 = {
        "data": {
            "repository": {
                "name": "repository",
                "owner": {"login": "organization"},
                "releases": {
                    "nodes": [make_release(1, "v1.0", "2022-02-01T00:00:00Z")],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor_1"},
                },
            }
        }
    }
    page2 = {
        "data": {
            "repository": {
                "name": "repository",
                "owner": {"login": "organization"},
                "releases": {
                    "nodes": [make_release(2, "v2.0", "2022-03-01T00:00:00Z")],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }
    }
    requests_mock.post("https://api.github.com/graphql", [{"json": page1}, {"json": page2}])
    stream = Releases(**repository_args)
    records = list(read_full_refresh(stream))
    assert len(records) == 2
    assert records[0]["id"] == 1
    assert records[0]["tag_name"] == "v1.0"
    assert records[1]["id"] == 2
    assert records[1]["tag_name"] == "v2.0"


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

    with patch.object(backoff_strategy, "backoff_time", return_value=0.01), pytest.raises(AirbyteTracedException):
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


# === Tests for error-swallowing bug fixes (oncall/issues/11907) ===


@patch("time.sleep")
def test_github_stream_abc_read_records_reraises_when_no_exception_attr(time_mock):
    """Bug fix: GithubStreamABC.read_records() guard clause uses `or` so that when
    AirbyteTracedException has no _exception attribute, the exception is re-raised
    immediately. With the old `and`, the second hasattr would raise AttributeError."""
    stream = ProbeStream(repositories=["org_name/repo"], page_size_for_large_streams=10)

    # Construct an AirbyteTracedException WITHOUT _exception attribute
    exc = AirbyteTracedException(message="bare error", failure_type=FailureType.system_error)
    # CDK sets _exception=None by default; delete it to simulate the case where it's truly absent
    delattr(exc, "_exception")
    assert not hasattr(exc, "_exception"), "Test precondition: exception must lack _exception attr"

    # Patch HttpStream.read_records (the super() target) to raise our bare exception
    with patch("airbyte_cdk.sources.streams.http.http.HttpStream.read_records", side_effect=exc):
        with pytest.raises(AirbyteTracedException):
            list(stream.read_records(stream_slice={"repository": "org_name/repo"}))


@patch("time.sleep")
def test_github_stream_abc_read_records_reraises_when_no_response_attr(time_mock):
    """Bug fix: GithubStreamABC.read_records() guard clause uses `or` so that when
    AirbyteTracedException has _exception but _exception lacks response attribute,
    the exception is re-raised. With the old `and`, this case was silently swallowed."""
    stream = ProbeStream(repositories=["org_name/repo"], page_size_for_large_streams=10)

    # Construct an AirbyteTracedException WITH _exception but WITHOUT response
    exc = AirbyteTracedException(message="missing response", failure_type=FailureType.system_error)
    inner = Exception("inner error")
    exc._exception = inner
    assert hasattr(exc, "_exception"), "Test precondition: exception must have _exception attr"
    assert not hasattr(exc._exception, "response"), "Test precondition: _exception must lack response attr"

    # Patch HttpStream.read_records (the super() target) to raise our exception
    with patch("airbyte_cdk.sources.streams.http.http.HttpStream.read_records", side_effect=exc):
        with pytest.raises(AirbyteTracedException):
            list(stream.read_records(stream_slice={"repository": "org_name/repo"}))


@patch("time.sleep")
def test_github_stream_abc_read_records_reraises_when_response_is_none(time_mock):
    """Bug fix (oncall/issues/11661): GithubStreamABC.read_records() must re-raise when the wrapped
    `requests.RequestException` has `response is None` (transport-layer failures such as
    ConnectionError, ConnectTimeout, ReadTimeout, SSLError, DNS failures). Previously, the
    guard only checked `hasattr(e._exception, "response")` — which is always True for
    `RequestException` subclasses — so `e._exception.response.status_code` raised
    `AttributeError: 'NoneType' object has no attribute 'status_code'`, masking the original
    transport error."""
    stream = ProbeStream(repositories=["org_name/repo"], page_size_for_large_streams=10)

    # Construct an AirbyteTracedException wrapping a ConnectionError with no response.
    exc = AirbyteTracedException(message="transport error", failure_type=FailureType.system_error)
    inner = requests.exceptions.ConnectionError("connection refused")
    exc._exception = inner
    assert hasattr(exc._exception, "response"), "Test precondition: RequestException always has `response`"
    assert exc._exception.response is None, "Test precondition: response must be None for transport errors"

    # Patch HttpStream.read_records (the super() target) to raise our exception
    with patch("airbyte_cdk.sources.streams.http.http.HttpStream.read_records", side_effect=exc):
        # The original AirbyteTracedException must propagate — NOT AttributeError.
        with pytest.raises(AirbyteTracedException):
            list(stream.read_records(stream_slice={"repository": "org_name/repo"}))


def test_releases_extract_database_id_does_not_catch_type_error():
    """Bug fix: _extract_database_id_from_node_id() should only catch ValueError,
    struct.error, and binascii.Error — not all exceptions. A TypeError (or other
    unexpected exception) should propagate instead of being silently swallowed."""

    # Passing a non-string type that has an underscore representation but causes
    # TypeError during string operations
    class BadNodeId:
        """Object that contains underscore but causes TypeError on split."""

        def __contains__(self, item):
            return True  # "_" in BadNodeId() returns True

        def split(self, *args, **kwargs):
            raise TypeError("split not supported")

    with pytest.raises(TypeError):
        Releases._extract_database_id_from_node_id(BadNodeId())


@pytest.mark.parametrize(
    "node_id,expected_id",
    [
        pytest.param("RA_####", None, id="invalid_base64_caught_by_binascii_error"),
        pytest.param("RA_ab", None, id="short_decoded_data"),
    ],
)
def test_releases_extract_database_id_catches_expected_errors(node_id, expected_id):
    """Verify that expected decode/unpack errors still return None after narrowing the except."""
    assert Releases._extract_database_id_from_node_id(node_id) == expected_id


# === Tests for defensive parse_response (airbyte-internal-issues/issues/16281) ===


def _make_response(status_code=200, json_data=None, text=None):
    """Build a mock `requests.Response` with controllable `.json()` and `.text`."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if text is not None:
        resp.text = text
        resp.json = MagicMock(side_effect=ValueError("No JSON"))
    elif json_data is not None:
        resp.text = json.dumps(json_data)
        resp.json = MagicMock(return_value=json_data)
    else:
        resp.text = ""
        resp.json = MagicMock(side_effect=ValueError("No JSON"))
    return resp


_REPO_ARGS = {"repositories": ["org/repo"], "page_size_for_large_streams": 30}
_STREAM_SLICE = {"repository": "org/repo"}


# === Tests for defensive error handlers (airbyte-internal-issues/issues/16281) ===


@pytest.mark.parametrize(
    "status_code,text,expected",
    [
        pytest.param(409, '{"message": "Git Repository is empty."}', True, id="conflict_empty_repo"),
        pytest.param(409, '{"message": "other"}', False, id="conflict_other_message"),
        pytest.param(409, "<html>Error</html>", False, id="conflict_html_body"),
        pytest.param(409, "", False, id="conflict_empty_body"),
        pytest.param(200, '{"message": "Git Repository is empty."}', False, id="non_409_status"),
    ],
)
def test_is_conflict_with_empty_repository_defensive(status_code, text, expected):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    if text:
        try:
            parsed = json.loads(text)
            resp.json = MagicMock(return_value=parsed)
        except json.JSONDecodeError:
            resp.json = MagicMock(side_effect=ValueError("No JSON"))
    else:
        resp.json = MagicMock(side_effect=ValueError("No JSON"))
    assert is_conflict_with_empty_repository(resp) == expected


def test_graphql_rate_limit_check_with_html_response():
    """GithubStreamABCErrorHandler should not crash when response is non-JSON
    during graphql rate limit check."""
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    handler = stream.get_error_handler()
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Resource": "graphql"}
    resp.text = "<html>Error</html>"
    resp.ok = True
    resp.json = MagicMock(side_effect=ValueError("No JSON"))
    result = handler.interpret_response(resp)
    assert result.response_action != ResponseAction.RATE_LIMITED


def test_graphql_error_handler_with_html_response():
    """GitHubGraphQLErrorHandler._safe_json_get_errors should not crash on non-JSON."""
    stream = MagicMock()
    stream.name = "test_stream"
    stream.large_stream = False
    stream.page_size = 100
    handler = GitHubGraphQLErrorHandler(stream=stream, logger=MagicMock(), error_mapping={})
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.headers = {}
    resp.text = "<html>Error</html>"
    resp.ok = True
    resp.json = MagicMock(side_effect=ValueError("No JSON"))
    assert handler._safe_json_get_errors(resp) is False


def test_graphql_error_handler_with_valid_errors():
    """GitHubGraphQLErrorHandler._safe_json_get_errors returns True when errors present."""
    handler = GitHubGraphQLErrorHandler(stream=MagicMock(), logger=MagicMock(), error_mapping={})
    resp = MagicMock(spec=requests.Response)
    resp.json = MagicMock(return_value={"errors": [{"type": "SOME_ERROR"}]})
    assert handler._safe_json_get_errors(resp) is True


def test_graphql_rate_limit_check_with_valid_rate_limited_body():
    """When response has graphql rate-limit header AND a valid body with RATE_LIMITED error,
    handler should return RATE_LIMITED action."""
    stream = ProbeStream(repositories=["test_repo"], page_size_for_large_streams=30)
    handler = stream.get_error_handler()
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.headers = {"X-RateLimit-Resource": "graphql"}
    resp.text = '{"errors": [{"type": "RATE_LIMITED"}]}'
    resp.ok = True
    resp.json = MagicMock(return_value={"errors": [{"type": "RATE_LIMITED"}]})
    result = handler.interpret_response(resp)
    assert result.response_action == ResponseAction.RATE_LIMITED


def test_releases_marked_as_large_stream():
    """The Releases GraphQL query is high-cost, so the stream must be marked as
    large_stream so that page_size defaults to the smaller large-stream value."""
    assert Releases.large_stream is True
    stream = Releases(
        repositories=["org/repo"],
        page_size_for_large_streams=constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM,
        start_date="2022-01-01T00:00:00Z",
    )
    assert stream.page_size == constants.DEFAULT_PAGE_SIZE_FOR_LARGE_STREAM


@pytest.mark.parametrize("status_code", [requests.codes.BAD_GATEWAY, requests.codes.GATEWAY_TIMEOUT])
def test_graphql_error_handler_502_504_message_includes_stream_name(status_code):
    """502/504 responses should produce an error message that names the stream and
    explains that the page size is being reduced — not the generic
    'Response status code: 504. Retrying...' string."""
    stream = MagicMock()
    stream.name = "releases"
    stream.large_stream = True
    stream.page_size = 10
    handler = GitHubGraphQLErrorHandler(stream=stream, logger=MagicMock(), error_mapping={})
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.headers = {}
    resp.text = ""
    resp.ok = False
    resp.json = MagicMock(return_value={})
    resolution = handler.interpret_response(resp)
    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.failure_type == FailureType.transient_error
    assert "`releases`" in resolution.error_message
    assert str(status_code) in resolution.error_message
    assert "Reducing GraphQL page size" in resolution.error_message


def test_graphql_error_handler_504_floors_page_size_at_one():
    """The 502/504 page-size halving must never let page_size drop below 1.
    A page_size of 0 would request no records and stall the stream."""
    stream = MagicMock()
    stream.name = "releases"
    stream.large_stream = True
    stream.page_size = 1
    handler = GitHubGraphQLErrorHandler(stream=stream, logger=MagicMock(), error_mapping={})
    resp = MagicMock(spec=requests.Response)
    resp.status_code = requests.codes.GATEWAY_TIMEOUT
    resp.headers = {}
    resp.text = ""
    resp.ok = False
    resp.json = MagicMock(return_value={})
    handler.interpret_response(resp)
    assert stream.page_size == 1


@patch("time.sleep")
def test_read_records_504_message_for_releases(time_mock, caplog, requests_mock):
    """After exhausting retries on 504s, the final user-facing log message for the
    Releases stream should name the stream and mention the page-size remediation —
    not the bare 'Response status code: 504. Retrying...' string."""
    stream = Releases(
        repositories=["org/repo"],
        page_size_for_large_streams=10,
        start_date="2022-01-01T00:00:00Z",
    )
    requests_mock.post(
        "https://api.github.com/graphql",
        status_code=requests.codes.GATEWAY_TIMEOUT,
        json={"message": "Gateway Timeout"},
    )
    list(read_full_refresh(stream))
    assert any(
        "GitHub returned HTTP 504 Gateway Timeout for stream `releases`" in msg and "Page size for large streams" in msg
        for msg in caplog.messages
    )


class _RequestLoopDetected(Exception):
    """Raised by a mock instead of letting an unterminated read spin forever."""


@patch("time.sleep")
def test_read_records_404_closes_resumable_full_refresh_slice(time_mock, requests_mock):
    """A swallowed 404 must terminate the partition instead of being retried forever.

    `ProbeStream` is full refresh, so it carries a `SubstreamResumableFullRefreshCursor`. Before the
    fix the swallowed error left the partition's cursor state empty, the checkpoint reader
    handed the same partition back on every iteration, and the sync emitted no records until
    the platform's source heartbeat killed the attempt.
    """
    calls = 0

    def request_callback(request, context):
        nonlocal calls
        calls += 1
        # 1 initial attempt + GithubStreamABC.max_retries (5); anything beyond that means the
        # partition was handed back for another pass.
        if calls > 6:
            raise _RequestLoopDetected(f"partition re-read after {calls} requests")
        context.status_code = HTTPStatus.NOT_FOUND
        return {"message": "Not Found"}

    requests_mock.get("https://api.github.com/repos/octocat/repo/probe_stream", json=request_callback)

    stream = ProbeStream(repositories=["octocat/repo"], page_size_for_large_streams=10)
    records = list(stream.read_only_records())

    assert records == []
    assert calls == 6
    assert stream.get_cursor().get_stream_state() == {
        "states": [{"partition": {"repository": "octocat/repo"}, "cursor": {"__ab_full_refresh_sync_complete": True}}]
    }


@patch("time.sleep")
def test_read_records_404_on_a_parent_read_leaves_shared_cursor_untouched(time_mock, requests_mock):
    """A swallowed error on a slice with no `partition` key must not close an empty partition.

    Substreams such as `Commits` read their parent (`Branches`) by calling `read_records` straight
    from `stream_slices()`, passing a bare mapping. A parent that is also in the catalog emits its
    own STATE, so closing `_extract_slice_fields`' `{}` fallback would publish a `{"partition": {}}`
    entry that means nothing.
    """
    requests_mock.get(
        "https://api.github.com/repos/octo-org/repo/probe_stream", status_code=HTTPStatus.NOT_FOUND, json={"message": "Not Found"}
    )

    stream = ProbeStream(repositories=["octo-org/repo"], page_size_for_large_streams=10)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"repository": "octo-org/repo"}))

    assert records == []
    # No `{"partition": {}}` entry: the empty partition was never closed.
    assert stream.get_cursor().get_stream_state() == {"states": []}

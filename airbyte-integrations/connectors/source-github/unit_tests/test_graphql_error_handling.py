#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_github.errors_handlers import (
    GRAPHQL_CONFIG_ERROR_TYPES,
    GRAPHQL_IGNORE_TYPES,
    GRAPHQL_RETRYABLE_TYPES,
    GitHubGraphQLErrorHandler,
    classify_graphql_errors,
)
from source_github.streams import (
    IssueReactions,
    ProjectsV2,
    PullRequestCommentReactions,
    PullRequestStats,
    Releases,
    Reviews,
)

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction


# ---------------------------------------------------------------------------
# classify_graphql_errors
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "errors,expected",
    [
        pytest.param([], "NONE", id="empty_errors"),
        pytest.param([{"type": "RATE_LIMITED"}], "RETRY", id="rate_limited"),
        pytest.param([{"type": "NOT_FOUND"}], "IGNORE", id="not_found"),
        pytest.param([{"type": "FORBIDDEN"}], "CONFIG_ERROR", id="forbidden"),
        pytest.param([{"type": "INSUFFICIENT_SCOPES"}], "CONFIG_ERROR", id="insufficient_scopes"),
        pytest.param([{"type": "MAX_NODE_LIMIT_EXCEEDED"}], "CONFIG_ERROR", id="max_node_limit"),
        pytest.param(
            [{"type": "NOT_FOUND"}, {"type": "FORBIDDEN"}],
            "CONFIG_ERROR",
            id="not_found_plus_forbidden_most_fatal_wins",
        ),
        pytest.param(
            [{"type": "NOT_FOUND"}, {"type": "RATE_LIMITED"}],
            "RETRY",
            id="not_found_plus_rate_limited_retryable_wins",
        ),
        pytest.param(
            [{"message": "Query exceeded resource limits"}],
            "RETRY",
            id="exceeded_resource_limits_message",
        ),
        pytest.param(
            [{"message": "Something timed out during execution"}],
            "RETRY",
            id="timed_out_message",
        ),
        pytest.param(
            [{"type": "UNKNOWN_NEW_TYPE"}],
            "RETRY",
            id="unknown_type_fallback_retry",
        ),
        pytest.param(
            [{"type": "NOT_FOUND"}, {"type": "UNKNOWN_NEW_TYPE"}],
            "RETRY",
            id="not_found_plus_unknown_fallback_retry",
        ),
    ],
)
def test_classify_graphql_errors(errors, expected):
    assert classify_graphql_errors(errors) == expected


# ---------------------------------------------------------------------------
# GitHubGraphQLErrorHandler.interpret_response
# ---------------------------------------------------------------------------
def _make_graphql_stream():
    """Create a minimal Releases stream for error handler tests."""
    return Releases(
        repositories=["test_owner/test_repo"],
        page_size_for_large_streams=10,
        start_date="2021-01-01T00:00:00Z",
    )


def _make_response(status_code, body, headers=None):
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.headers = headers or {}
    response.text = json.dumps(body)
    response.ok = status_code == 200
    response.json = lambda: body
    return response


def test_graphql_not_found_returns_ignore():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "NOT_FOUND", "message": "Not found", "path": ["repository"]}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.IGNORE
    assert result.failure_type == FailureType.config_error
    assert "NOT_FOUND" in result.error_message


def test_graphql_forbidden_returns_fail():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "FORBIDDEN", "message": "access denied"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == FailureType.config_error
    assert "denied access" in result.error_message


def test_graphql_insufficient_scopes_returns_fail():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "INSUFFICIENT_SCOPES", "message": "need repo scope"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == FailureType.config_error
    assert "missing required scopes" in result.error_message


def test_graphql_max_node_limit_returns_fail():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "MAX_NODE_LIMIT_EXCEEDED", "message": "too many nodes"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.FAIL
    assert result.failure_type == FailureType.config_error
    assert "500,000 total nodes" in result.error_message


def test_graphql_rate_limited_returns_retry():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "RATE_LIMITED"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.RETRY
    assert result.failure_type == FailureType.transient_error


def test_graphql_502_halves_page_size():
    stream = _make_graphql_stream()
    original_page_size = stream.page_size
    handler = stream.get_error_handler()
    response = _make_response(502, {})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.RETRY
    assert result.failure_type == FailureType.transient_error
    assert stream.page_size == max(1, int(original_page_size / 2))


def test_graphql_no_errors_falls_through():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"data": {"repository": {}}})
    result = handler.interpret_response(response)
    # 200 with no errors should succeed
    assert result.response_action == ResponseAction.SUCCESS


def test_graphql_unknown_error_type_retries():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"type": "SOME_NEW_ERROR"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.RETRY
    assert result.failure_type == FailureType.transient_error


def test_graphql_timed_out_message_retries():
    stream = _make_graphql_stream()
    handler = stream.get_error_handler()
    response = _make_response(200, {"errors": [{"message": "Something timed out"}]})
    result = handler.interpret_response(response)
    assert result.response_action == ResponseAction.RETRY
    assert result.failure_type == FailureType.transient_error


# ---------------------------------------------------------------------------
# parse_response warning on missing data.repository
# ---------------------------------------------------------------------------
GRAPHQL_STREAM_CLASSES = [
    pytest.param(Releases, id="Releases"),
    pytest.param(PullRequestStats, id="PullRequestStats"),
    pytest.param(Reviews, id="Reviews"),
    pytest.param(ProjectsV2, id="ProjectsV2"),
    pytest.param(IssueReactions, id="IssueReactions"),
]


@pytest.mark.parametrize("stream_cls", GRAPHQL_STREAM_CLASSES)
def test_parse_response_warns_when_repository_is_none(stream_cls, caplog):
    stream = stream_cls(
        repositories=["test_owner/test_repo"],
        page_size_for_large_streams=10,
        start_date="2021-01-01T00:00:00Z",
    )
    body = {"data": {"repository": None}, "errors": [{"type": "NOT_FOUND", "message": "not found"}]}
    response = _make_response(200, body)

    with caplog.at_level(logging.WARNING):
        records = list(stream.parse_response(response))

    assert records == []
    assert any("no `data.repository`" in msg for msg in caplog.messages)


def test_pull_request_comment_reactions_warns_when_no_data(caplog):
    """PullRequestCommentReactions checks both repository and node."""
    stream = PullRequestCommentReactions(
        repositories=["test_owner/test_repo"],
        page_size_for_large_streams=10,
        start_date="2021-01-01T00:00:00Z",
    )
    body = {"data": {"repository": None, "node": None}, "errors": [{"type": "NOT_FOUND"}]}
    response = _make_response(200, body)

    with caplog.at_level(logging.WARNING):
        records = list(stream.parse_response(response))

    assert records == []
    assert any("no `data.repository` or `data.node`" in msg for msg in caplog.messages)

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pendulum as pdm
import pytest
import requests
from source_sentry.streams import Events, Issues, ProjectDetail, Projects, SentryIncremental, SentryStreamPagination

INIT_ARGS = {"hostname": "sentry.io", "organization": "test-org", "project": "test-project"}


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(SentryStreamPagination, "path", "test_endpoint")
    mocker.patch.object(SentryStreamPagination, "__abstractmethods__", set())


def test_next_page_token(patch_base_class):
    stream = SentryStreamPagination(hostname="sentry.io")
    resp = MagicMock()
    cursor = "next_page_num"
    resp.links = {"next": {"results": "true", "cursor": cursor}}
    inputs = {"response": resp}
    expected_token = {"cursor": cursor}
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_is_none(patch_base_class):
    stream = SentryStreamPagination(hostname="sentry.io")
    resp = MagicMock()
    resp.links = {"next": {"results": "false", "cursor": "no_next"}}
    inputs = {"response": resp}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def next_page_token_inputs():
    links_headers = [
        {},
        {"next": {}},
    ]
    responses = [MagicMock() for _ in links_headers]
    for mock, header in zip(responses, links_headers):
        mock.links = header

    return responses


@pytest.mark.parametrize("response", next_page_token_inputs())
def test_next_page_token_raises(patch_base_class, response):
    stream = SentryStreamPagination(hostname="sentry.io")
    inputs = {"response": response}
    with pytest.raises(KeyError):
        stream.next_page_token(**inputs)


def test_events_path():
    stream = Events(**INIT_ARGS)
    expected = "projects/test-org/test-project/events/"
    assert stream.path() == expected


def test_issues_path():
    stream = Issues(**INIT_ARGS)
    expected = "projects/test-org/test-project/issues/"
    assert stream.path() == expected


def test_projects_path():
    stream = Projects(hostname="sentry.io")
    expected = "projects/"
    assert stream.path() == expected


def test_project_detail_path():
    stream = ProjectDetail(**INIT_ARGS)
    expected = "projects/test-org/test-project/"
    assert stream.path() == expected


def test_sentry_stream_pagination_request_params(patch_base_class):
    stream = SentryStreamPagination(hostname="sentry.io")
    expected = {"cursor": "next-page"}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_events_request_params():
    stream = Events(**INIT_ARGS)
    expected = {"cursor": "next-page", "full": "true"}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_issues_request_params():
    stream = Issues(**INIT_ARGS)
    expected = {"cursor": "next-page", "statsPeriod": "", "query": "lastSeen:>1900-01-01T00:00:00Z"}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_projects_request_params():
    stream = Projects(hostname="sentry.io")
    expected = {"cursor": "next-page"}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_project_detail_request_params():
    stream = ProjectDetail(**INIT_ARGS)
    expected = {}
    assert stream.request_params(stream_state=None, next_page_token=None) == expected

def test_issues_parse_response(mocker):
    with patch('source_sentry.streams.Issues._get_cursor_value') as mock_get_cursor_value:
      stream = Issues(**INIT_ARGS)
      mock_get_cursor_value.return_value = "time"
      state = {}
      response = requests.Response()
      mocker.patch.object(response, "json", return_value=[{"id": "1"}])
      result = list(stream.parse_response(response, state))
      assert result[0] == {"id": "1"}

def test_project_detail_parse_response(mocker):
    stream = ProjectDetail(organization="test_org", project="test_proj", hostname="sentry.io")
    response = requests.Response()
    response.json = Mock(return_value={"id": "1"})
    result = list(stream.parse_response(response))
    assert result[0] == {"id": "1"}

class MockSentryIncremental(SentryIncremental):
    def path():
        return '/test/path'

def test_sentry_incremental_parse_response(mocker):
    with patch('source_sentry.streams.SentryIncremental.filter_by_state') as mock_filter_by_state:
      stream = MockSentryIncremental(hostname="sentry.io")
      mock_filter_by_state.return_value = True
      state = None
      response = requests.Response()
      mocker.patch.object(response, "json", return_value=[{"id": "1"}])
      mock_filter_by_state.return_value = iter(response.json())
      result = list(stream.parse_response(response, state))
      print(result)
      assert result[0] == {"id": "1"}


@pytest.mark.parametrize(
    "state, expected",
    [
        ({}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": ""}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": "None"}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": "2023-01-01T00:00:00.0Z"}, "2023-01-01T00:00:00.0Z"),
    ],
    ids=[
        "No State",
        "State is Empty String",
        "State is 'None'",
        "State is present",
    ],
)
def test_validate_state_value(state, expected):
    stream = Events(**INIT_ARGS)
    state_value = state.get(stream.cursor_field)
    assert stream.validate_state_value(state_value) == expected


@pytest.mark.parametrize(
    "state, expected",
    [
        ({}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": ""}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": "None"}, "1900-01-01T00:00:00.0Z"),
        ({"dateCreated": "2023-01-01T00:00:00.0Z"}, "2023-01-01T00:00:00.0Z"),
    ],
    ids=[
        "No State",
        "State is Empty String",
        "State is 'None'",
        "State is present",
    ],
)
def test_get_state_value(state, expected):
    stream = Events(**INIT_ARGS)
    # we expect the datetime object out of get_state_value method.
    assert stream.get_state_value(state) == pdm.parse(expected)

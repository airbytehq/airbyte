#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_protocol.models import SyncMode
from source_sentry import SourceSentry

INIT_ARGS = {"hostname": "sentry.io", "organization": "test-org", "project": "test-project"}


def get_stream_by_name(stream_name):
    streams = SourceSentry().streams(config=INIT_ARGS)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def test_next_page_token():
    stream = get_stream_by_name("events")
    response_mock = MagicMock()
    response_mock.headers = {}
    response_mock.links = {"next": {"cursor": "next-page"}}
    assert stream.retriever.paginator.pagination_strategy.next_page_token(response=response_mock, last_records=[]) == "next-page"


def test_next_page_token_is_none():
    stream = get_stream_by_name("events")
    response_mock = MagicMock()
    response_mock.headers = {}
    # stop condition: "results": "false"
    response_mock.links = {"next": {"cursor": "", "results": "false"}}
    assert stream.retriever.paginator.pagination_strategy.next_page_token(response=response_mock, last_records=[]) is None


def test_events_path():
    stream = get_stream_by_name("events")
    expected = "projects/test-org/test-project/events/"
    assert stream.retriever.requester.get_path(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_issues_path():
    stream = get_stream_by_name("issues")
    expected = "projects/test-org/test-project/issues/"
    assert stream.retriever.requester.get_path(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_projects_path():
    stream = get_stream_by_name("projects")
    expected = "projects/"
    assert stream.retriever.requester.get_path(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_project_detail_path():
    stream = get_stream_by_name("project_detail")
    expected = "projects/test-org/test-project/"
    assert stream.retriever.requester.get_path(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_events_request_params():
    stream = get_stream_by_name("events")
    assert stream.retriever.requester.get_request_params(stream_state=None, stream_slice=None, next_page_token=None) == {"full": "true"}


def test_issues_request_params():
    stream = get_stream_by_name("issues")
    expected = {"query": "lastSeen:>1900-01-01T00:00:00.0Z"}
    assert stream.retriever.requester.get_request_params(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_projects_request_params():
    stream = get_stream_by_name("projects")
    expected = "next-page"
    response_mock = MagicMock()
    response_mock.headers = {}
    response_mock.links = {"next": {"cursor": expected}}
    assert stream.retriever.paginator.pagination_strategy.next_page_token(response=response_mock, last_records=[]) == expected


def test_project_detail_request_params():
    stream = get_stream_by_name("project_detail")
    expected = {}
    assert stream.retriever.requester.get_request_params(stream_state=None, stream_slice=None, next_page_token=None) == expected


def test_project_detail_parse_response(requests_mock):
    expected = {"id": "1", "name": "test project"}
    stream = get_stream_by_name("project_detail")
    requests_mock.get(
        "https://sentry.io/api/0/projects/test-org/test-project/",
        json=expected
    )
    result = list(stream.read_records(sync_mode=SyncMode.full_refresh))[0]
    assert expected == result.data


@pytest.mark.parametrize(
    "state, expected",
    [
        ({}, None),
        ({"dateCreated": ""}, None),
        ({"dateCreated": "2023-01-01T00:00:00.0Z"}, "2023-01-01T00:00:00.0Z"),
    ],
    ids=[
        "No State",
        "State is Empty String",
        "State is present",
    ],
)
def test_events_validate_state_value(state, expected):
    # low code cdk sets state to none if it does not exist, py version used 1900-01-01 as state in this case.
    # Instead, record condition will pass all records that were fetched and state will be updated after.
    stream = get_stream_by_name("events")
    stream.retriever.state = state
    assert stream.state.get(stream.cursor_field) == expected


@pytest.mark.parametrize(
    "state, expected",
    [
        ({}, None),
        ({"lastSeen": ""}, None),
        ({"lastSeen": "2023-01-01T00:00:00.0Z"}, "2023-01-01T00:00:00.0Z"),
    ],
    ids=[
        "No State",
        "State is Empty String",
        "State is present",
    ],
)
def test_issues_validate_state_value(state, expected):
    # low code cdk sets state to none if it does not exist, py version used 1900-01-01 as state in this case.
    # Instead, record condition will pass all records that were fetched and state will be updated after.
    stream = get_stream_by_name("issues")
    stream.retriever.state = state
    assert stream.state.get(stream.cursor_field) == expected


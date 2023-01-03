#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_sentry.streams import Events, Issues, ProjectDetail, Projects, SentryStreamPagination

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
    expected = {"cursor": "next-page", "statsPeriod": "", "query": ""}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_projects_request_params():
    stream = Projects(hostname="sentry.io")
    expected = {"cursor": "next-page"}
    assert stream.request_params(stream_state=None, next_page_token={"cursor": "next-page"}) == expected


def test_project_detail_request_params():
    stream = ProjectDetail(**INIT_ARGS)
    expected = {}
    assert stream.request_params(stream_state=None, next_page_token=None) == expected

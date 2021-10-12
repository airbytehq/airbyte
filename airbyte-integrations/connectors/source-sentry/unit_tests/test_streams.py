#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_sentry.streams import Events, Issues, ProjectDetail, SentryStream

INIT_ARGS = {"hostname": "sentry.io", "organization": "test-org", "project": "test-project"}


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(SentryStream, "path", "test_endpoint")
    mocker.patch.object(SentryStream, "primary_key", "test_primary_key")
    mocker.patch.object(SentryStream, "__abstractmethods__", set())


def test_next_page_token(patch_base_class):
    stream = SentryStream(**INIT_ARGS)
    resp = MagicMock()
    cursor = "next_page_num"
    resp.links = {"next": {"results": "true", "cursor": cursor}}
    inputs = {"response": resp}
    expected_token = {"cursor": cursor}
    assert stream.next_page_token(**inputs) == expected_token


def next_page_token_inputs():
    links_headers = [
        {},
        {"next": {}},
        {"next": {"results": "false", "cursor": "no_next"}},
    ]
    responses = [MagicMock() for _ in links_headers]
    for mock, header in zip(responses, links_headers):
        mock.links = header

    return responses


@pytest.mark.parametrize("response", next_page_token_inputs())
def test_next_page_token_is_none(patch_base_class, response):
    stream = SentryStream(**INIT_ARGS)
    inputs = {"response": response}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_events_path():
    stream = Events(**INIT_ARGS)
    expected = "projects/test-org/test-project/events/"
    assert stream.path() == expected


def test_issues_path():
    stream = Issues(**INIT_ARGS)
    expected = "projects/test-org/test-project/issues/"
    assert stream.path() == expected


def test_project_detail_path():
    stream = ProjectDetail(**INIT_ARGS)
    expected = "projects/test-org/test-project/"
    assert stream.path() == expected

#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import BaseBackoffException
from source_github.streams import Projects, PullRequestCommentReactions

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
def test_projects_disabled():
    kwargs = {"start_date": "start_date", "page_size_for_large_streams": 30, "repositories": ["test_repo"]}
    stream = Projects(**kwargs)

    responses.add(
        "GET",
        "https://api.github.com/repos/test_repo/projects",
        status=requests.codes.GONE,
        json={"message": "Projects are disabled for this repository", "documentation_url": "https://docs.github.com/v3/projects"},
    )

    slices = stream.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records = list(stream.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh))
        assert records == []

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.github.com/repos/test_repo/projects?per_page=100&state=all"

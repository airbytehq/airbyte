#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import patch

import pytest
import responses
from airbyte_cdk.sources.streams.http.exceptions import BaseBackoffException
from source_github.streams import PullRequestCommentReactions

DEFAULT_BACKOFF_DELAYS = [5, 10, 20, 40, 80]


@responses.activate
@patch("time.sleep")
def test_bad_gateway_retry(time_mock):
    args = {"authenticator": None, "repositories": ["test_repo"], "start_date": "start_date", "page_size_for_large_streams": 30}
    stream = PullRequestCommentReactions(**args)
    stream_slice = {"repository": "test_repo", "id": "id"}

    responses.add(
        "GET",
        "https://api.github.com/repos/test_repo/pulls/comments/id/reactions",
        status=HTTPStatus.BAD_GATEWAY,
        json={"message": "Bad request"},
    )
    with pytest.raises(BaseBackoffException):
        list(stream.read_records(sync_mode="full_refresh", stream_slice=stream_slice))

    sleep_delays = [delay[0][0] for delay in time_mock.call_args_list]
    assert sleep_delays == DEFAULT_BACKOFF_DELAYS

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

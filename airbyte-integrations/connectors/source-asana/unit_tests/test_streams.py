#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import requests_mock as req_mock
from airbyte_cdk.models import SyncMode
from source_asana.streams import AsanaStream, Sections, Stories, Tags, Tasks, TeamMemberships, Users


@pytest.mark.parametrize(
    "stream",
    [Tasks, Sections, Users, TeamMemberships, Tags, Stories],
)
def test_task_stream(requests_mock, stream, mock_response):
    requests_mock.get(req_mock.ANY, json=mock_response)
    instance = stream(authenticator=MagicMock())

    stream_slice = next(instance.stream_slices(sync_mode=SyncMode.full_refresh))
    record = next(instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert record


@patch.multiple(AsanaStream, __abstractmethods__=set())
def test_next_page_token():
    stream = AsanaStream()
    inputs = {"response": MagicMock()}
    expected = "offset"
    assert expected in stream.next_page_token(**inputs)


@pytest.mark.parametrize(
    ("http_status_code", "should_retry"),
    [
        (402, False),
        (403, False),
        (404, False),
        (451, False),
        (429, True),
    ],
)
def test_should_retry(http_status_code, should_retry):
    """
    402, 403, 404, 451 - should not retry.
    429 - should retry.
    """
    response_mock = MagicMock()
    response_mock.status_code = http_status_code
    stream = Stories(MagicMock())
    assert stream.should_retry(response_mock) == should_retry

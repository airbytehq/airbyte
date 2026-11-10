# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Pagination contract shared by all nine v1 list streams.

Pennylane v1 list responses carry `current_page` and `total_pages`. Pagination
must follow `total_pages` rather than stopping on a short page, so a server-side
`per_page` cap below the requested size cannot truncate a stream to page 1.
"""

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.helpers import read_stream
from mock_server.request_builder import STREAMS, StreamSpec, list_request, list_response, record


_START_TIME = "2024-01-01T00:00:00Z"
_FILTER_LOWER_BOUND = "2024-01-01T00:00:00.000000Z"


def _updated_since(stream: StreamSpec):
    return _FILTER_LOWER_BOUND if stream.incremental else None


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize("stream", STREAMS, ids=[stream.name for stream in STREAMS])
def test_short_first_page_is_followed_until_total_pages(stream: StreamSpec) -> None:
    with HttpMocker() as http_mocker:
        page_1 = list_request(stream, page=1, updated_since=_updated_since(stream))
        page_2 = list_request(stream, page=2, updated_since=_updated_since(stream))
        # Page 1 is shorter than per_page (as when the server caps the page size) but is not the last page.
        http_mocker.get(page_1, list_response(stream, [record(stream, "1"), record(stream, "2")], current_page=1, total_pages=2))
        http_mocker.get(page_2, list_response(stream, [record(stream, "3")], current_page=2, total_pages=2))

        output = read_stream(stream.name, SyncMode.full_refresh, ConfigBuilder().with_start_time(_START_TIME).build())

        assert output.errors == []
        assert [message.record.data[stream.primary_key] for message in output.records] == ["1", "2", "3"]
        http_mocker.assert_number_of_calls(page_1, 1)
        http_mocker.assert_number_of_calls(page_2, 1)


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize("stream", STREAMS, ids=[stream.name for stream in STREAMS])
def test_full_last_page_stops_pagination(stream: StreamSpec) -> None:
    with HttpMocker() as http_mocker:
        only_page = list_request(stream, page=1, updated_since=_updated_since(stream))
        full_page = [record(stream, str(index)) for index in range(100)]
        # A full page that is also the last page must not trigger a request for page 2 (which is not mocked).
        http_mocker.get(only_page, list_response(stream, full_page, current_page=1, total_pages=1))

        output = read_stream(stream.name, SyncMode.full_refresh, ConfigBuilder().with_start_time(_START_TIME).build())

        assert output.errors == []
        assert len(output.records) == 100
        http_mocker.assert_number_of_calls(only_page, 1)

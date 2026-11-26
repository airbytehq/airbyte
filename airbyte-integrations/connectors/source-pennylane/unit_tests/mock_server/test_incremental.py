# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Incremental contract for the seven `updated_at` streams.

The v1 API requires `filter` to be a bare JSON array of filter objects. These
tests pin the exact `filter` value sent on a first sync (lower bound from the
config `start_time`) and on a following sync (lower bound from the stored state),
and the state value emitted.
"""

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.helpers import read_stream
from mock_server.request_builder import INCREMENTAL_STREAMS, StreamSpec, list_request, list_response, record


_IDS = [stream.name for stream in INCREMENTAL_STREAMS]


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize("stream", INCREMENTAL_STREAMS, ids=_IDS)
def test_first_sync_filters_from_start_time_and_emits_latest_updated_at(stream: StreamSpec) -> None:
    with HttpMocker() as http_mocker:
        request = list_request(stream, page=1, updated_since="2024-01-01T00:00:00.000000Z")
        records = [
            record(stream, "1", updated_at="2024-02-01T10:00:00.000Z"),
            record(stream, "2", updated_at="2024-03-15T08:30:00.000Z"),
        ]
        http_mocker.get(request, list_response(stream, records, current_page=1, total_pages=1))

        output = read_stream(stream.name, SyncMode.incremental, ConfigBuilder().with_start_time("2024-01-01T00:00:00Z").build())

        assert output.errors == []
        assert [message.record.data[stream.primary_key] for message in output.records] == ["1", "2"]
        http_mocker.assert_number_of_calls(request, 1)
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": "2024-03-15T08:30:00.000000Z"}


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize("stream", INCREMENTAL_STREAMS, ids=_IDS)
def test_next_sync_filters_from_state_cursor(stream: StreamSpec) -> None:
    state = StateBuilder().with_stream_state(stream.name, {"updated_at": "2024-03-15T08:30:00.000000Z"}).build()
    with HttpMocker() as http_mocker:
        request = list_request(stream, page=1, updated_since="2024-03-15T08:30:00.000000Z")
        # The `gteq` filter is inclusive, so the record at the stored cursor is re-emitted alongside newer ones.
        records = [
            record(stream, "2", updated_at="2024-03-15T08:30:00.000Z"),
            record(stream, "3", updated_at="2024-04-02T12:00:00.000Z"),
        ]
        http_mocker.get(request, list_response(stream, records, current_page=1, total_pages=1))

        output = read_stream(stream.name, SyncMode.incremental, ConfigBuilder().with_start_time("2024-01-01T00:00:00Z").build(), state)

        assert output.errors == []
        assert [message.record.data[stream.primary_key] for message in output.records] == ["2", "3"]
        http_mocker.assert_number_of_calls(request, 1)
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": "2024-04-02T12:00:00.000000Z"}

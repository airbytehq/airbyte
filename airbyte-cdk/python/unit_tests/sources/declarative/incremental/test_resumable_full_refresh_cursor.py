# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.sources.declarative.incremental import ResumableFullRefreshCursor
from airbyte_cdk.sources.types import StreamSlice


@pytest.mark.parametrize(
    "stream_state, expected_slice",
    [
        pytest.param({"updated_at": "2024-04-30"}, StreamSlice(cursor_slice={"updated_at": "2024-04-30"}, partition={}), id="test_set_incoming_stream_state"),
        pytest.param({}, StreamSlice(cursor_slice={}, partition={}), id="test_empty_stream_state"),
    ]
)
def test_stream_slices(stream_state, expected_slice):
    cursor = ResumableFullRefreshCursor(parameters={})
    cursor.set_initial_state(stream_state=stream_state)

    actual_slices = [stream_slice for stream_slice in cursor.stream_slices()]

    assert actual_slices == [expected_slice]

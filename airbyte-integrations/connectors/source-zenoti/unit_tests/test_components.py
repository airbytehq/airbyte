#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.streams import Stream
from source_zenoti.components import (
    IncrementalSingleSliceCursor,
    IncrementalSubstreamSlicerCursor,
)

def test_slicer():
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    slicer.observe(date_time_dict, date_time_dict)
    slicer.close_slice(date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
            {"first_stream_cursor": 1662459010},
            {
                "first_stream_cursor": 1662459010,
                "parent_stream_name": {"state": {"parent_cursor_field": 1662459010}}
            },
            [{"first_stream_cursor": 1662459010}],
        )
    ],
)
def test_sub_slicer(last_record, expected, records):
    parent_stream = Mock(spec=Stream)
    parent_stream.name = "parent_stream_name"
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)
    parent_stream.retriever = Mock(spec=Retriever)
    parent_stream.retriever.state = {"state": {"parent_cursor_field": 1662459010}}

    parent_config = ParentStreamConfig(
        stream=parent_stream,
        parent_key="first_stream_cursor",
        partition_field="first_stream_id",
        parameters={},
        config={},
    )

    slicer = IncrementalSubstreamSlicerCursor(
        config={}, parameters={}, cursor_field="first_stream_cursor", parent_stream_configs=[parent_config], parent_complete_fetch=True
    )
    slicer.set_initial_state(expected)
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.observe(stream_slice, last_record)
    slicer.close_slice(stream_slice)
    assert slicer.get_stream_state() == expected

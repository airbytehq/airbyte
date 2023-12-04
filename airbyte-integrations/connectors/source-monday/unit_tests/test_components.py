#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.streams import Stream
from requests import Response
from source_monday.components import IncrementalSingleSlice, IncrementalSubstreamSlicer
from source_monday.extractor import MondayIncrementalItemsExtractor


def _create_response(content: Any) -> Response:
    response = Response()
    response._content = json.dumps(content).encode("utf-8")
    return response


def test_slicer():
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSlice(config={}, parameters={}, cursor_field="updated_at")
    slicer.close_slice(date_time_dict, date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
            {"first_stream_cursor": 1662459010},
            {"parent_stream_name": {"parent_cursor_field": 1662459010}, "first_stream_cursor": 1662459010},
            [{"first_stream_cursor": 1662459010}],
        ),
        (None, {}, []),
    ],
)
def test_sub_slicer(last_record, expected, records):
    parent_stream = Mock(spec=Stream)
    parent_stream.name = "parent_stream_name"
    parent_stream.cursor_field = "parent_cursor_field"
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)

    parent_config = ParentStreamConfig(
        stream=parent_stream,
        parent_key="id",
        partition_field="first_stream_id",
        parameters={},
        config={},
    )

    slicer = IncrementalSubstreamSlicer(
        config={}, parameters={}, cursor_field="first_stream_cursor", parent_stream_configs=[parent_config], nested_items_per_page=10
    )
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.close_slice(stream_slice, last_record)
    assert slicer.get_stream_state() == expected


def test_null_records(caplog):
    extractor = MondayIncrementalItemsExtractor(
        field_path=["data", "boards", "*"],
        config={},
        parameters={},
    )
    content = {
        "data": {
            "boards": [
                {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z"},
                {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z"},
                {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z"},
                {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z"},
                {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z"},
                {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z"},
                None,
                None,
            ]
        },
        "errors": [{"message": "Cannot return null for non-nullable field Board.creator"}],
        "account_id": 123456,
    }
    response = _create_response(content)
    records = extractor.extract_records(response)
    warning_message = "Record with null value received; errors: [{'message': 'Cannot return null for non-nullable field Board.creator'}]"
    assert warning_message in caplog.messages
    expected_records = [
        {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z", "updated_at_int": 1692095449},
        {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z", "updated_at_int": 1692095450},
        {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z", "updated_at_int": 1692095451},
        {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z", "updated_at_int": 1692095452},
        {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z", "updated_at_int": 1692095443},
        {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z", "updated_at_int": 1692095454},
    ]
    assert records == expected_records

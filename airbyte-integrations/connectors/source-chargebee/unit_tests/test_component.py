#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from source_chargebee.components import CustomFieldTransformation, IncrementalSingleSliceCursor


@pytest.mark.parametrize(
    "record, expected_record",
    [
        ({"pk": 1, "name": "example"}, {"pk": 1, "name": "example", "custom_fields": []}),
        (
            {"pk": 1, "name": "example", "cf_field1": "val1", "cf_field2": "val2"},
            {
                "pk": 1,
                "name": "example",
                "custom_fields": [{"name": "cf_field1", "value": "val1"}, {"name": "cf_field2", "value": "val2"}],
            },
        ),
    ],
    ids=["no_custom_field", "custom_field"],
)
def test_field_transformation(record, expected_record):
    transformer = CustomFieldTransformation()
    transformed_record = transformer.transform(record)
    assert transformed_record == expected_record

@pytest.mark.parametrize(
    "record_data, expected",
    [
        ({"pk": 1, "name": "example", "updated_at": 1662459011}, True),
    ]
)
def test_slicer(record_data, expected):
    date_time_dict = {"updated_at": 1662459010}
    new_state = {"updated_at": 1662459011}
    slicer = IncrementalSingleSliceCursor(cursor_field="updated_at", config={}, parameters={})
    stream_slice = StreamSlice(partition={}, cursor_slice=date_time_dict)
    record = Record(data=record_data, associated_slice=stream_slice)
    slicer.observe(StreamSlice(partition={}, cursor_slice=date_time_dict), record)
    slicer.close_slice(stream_slice)
    assert slicer.get_stream_state() == new_state
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_params() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "first_record, second_record, expected",
    [
        ({"pk": 1, "name": "example", "updated_at": 1662459010},
        {"pk": 2, "name": "example2", "updated_at": 1662460000},
        True),
        ({"pk": 1, "name": "example", "updated_at": 1662459010},
        {"pk": 2, "name": "example2", "updated_at": 1662440000},
        False),
        ({"pk": 1, "name": "example", "updated_at": 1662459010},
        {"pk": 2, "name": "example2"},
        False),
        ({"pk": 1, "name": "example"},
        {"pk": 2, "name": "example2", "updated_at": 1662459010},
        True),
    ]
)
def test_is_greater_than_or_equal(first_record, second_record, expected):
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    assert slicer.is_greater_than_or_equal(second_record, first_record) == expected

def test_set_initial_state():
    cursor_field = "updated_at"
    cursor_value = 999999999
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field=cursor_field)
    slicer.set_initial_state(stream_state={cursor_field: cursor_value})
    assert slicer._state[cursor_field] == cursor_value

@pytest.mark.parametrize(
    "record, expected",
    [
        ({"pk": 1, "name": "example", "updated_at": 1662459010},
        True),
    ]
)
def test_should_be_synced(record, expected):
    cursor_field = "updated_at"
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field=cursor_field)
    assert slicer.should_be_synced(record) == expected

def test_stream_slices():
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    stream_slices_instance = slicer.stream_slices()
    actual = next(stream_slices_instance)
    assert actual == {}

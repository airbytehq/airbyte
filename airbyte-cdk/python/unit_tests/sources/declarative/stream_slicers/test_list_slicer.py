#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer


@pytest.mark.parametrize(
    "test_name, slice_values, cursor_field, expected_slices",
    [
        (
            "test_single_element",
            ["customer", "store", "subscription"],
            "owner_resource",
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
        (
            "test_input_list_is_string",
            '["customer", "store", "subscription"]',
            "owner_resource",
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
    ],
)
def test_list_slicer(test_name, slice_values, cursor_field, expected_slices):
    slicer = ListStreamSlicer(slice_values, cursor_field, config={})
    slices = [s for s in slicer.stream_slices(SyncMode.incremental, stream_state=None)]
    assert slices == expected_slices


@pytest.mark.parametrize(
    "test_name, stream_slice, last_record, expected_state",
    [
        ("test_update_cursor_no_state_no_record", {}, None, None),
        ("test_update_cursor_with_state_no_record", {"owner_resource": "customer"}, None, {"owner_resource": "customer"}),
        ("test_update_cursor_value_not_in_list", {"owner_resource": "invalid"}, None, None),
    ],
)
def test_update_cursor(test_name, stream_slice, last_record, expected_state):
    slice_values = ["customer", "store", "subscription"]
    cursor_field = "owner_resource"
    slicer = ListStreamSlicer(slice_values, cursor_field, config={})
    slicer.update_cursor(stream_slice, last_record)
    updated_state = slicer.get_stream_state()
    assert expected_state == updated_state

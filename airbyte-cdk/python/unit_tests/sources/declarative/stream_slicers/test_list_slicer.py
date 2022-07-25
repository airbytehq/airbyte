#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer

slice_values = ["customer", "store", "subscription"]
cursor_field = "owner_resource"


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
        ("test_update_cursor_no_state_no_record", {}, None, {}),
        ("test_update_cursor_with_state_no_record", {"owner_resource": "customer"}, None, {"owner_resource": "customer"}),
        ("test_update_cursor_value_not_in_list", {"owner_resource": "invalid"}, None, {}),
    ],
)
def test_update_cursor(test_name, stream_slice, last_record, expected_state):
    slicer = ListStreamSlicer(slice_values, cursor_field, config={})
    slicer.update_cursor(stream_slice, last_record)
    updated_state = slicer.get_stream_state()
    assert expected_state == updated_state


@pytest.mark.parametrize(
    "test_name, request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            "test_inject_into_req_param",
            RequestOption(RequestOptionType.request_parameter, "owner_resource"),
            {"owner_resource": "customer"},
            {},
            {},
            {},
        ),
        ("test_pass_by_header", RequestOption(RequestOptionType.header, "owner_resource"), {}, {"owner_resource": "customer"}, {}, {}),
        (
            "test_inject_into_body_json",
            RequestOption(RequestOptionType.body_json, "owner_resource"),
            {},
            {},
            {"owner_resource": "customer"},
            {},
        ),
        (
            "test_inject_into_body_data",
            RequestOption(RequestOptionType.body_data, "owner_resource"),
            {},
            {},
            {},
            {"owner_resource": "customer"},
        ),
        (
            "test_inject_into_path",
            RequestOption(RequestOptionType.path),
            {},
            {},
            {},
            {"owner_resource": "customer"},
        ),
    ],
)
def test_request_option(test_name, request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    if request_option.inject_into == RequestOptionType.path:
        try:
            ListStreamSlicer(slice_values, cursor_field, {}, request_option)
            assert False
        except ValueError:
            return
    slicer = ListStreamSlicer(slice_values, cursor_field, {}, request_option)
    stream_slice = {cursor_field: "customer"}

    slicer.update_cursor(stream_slice)
    assert expected_req_params == slicer.request_params()
    assert expected_headers == slicer.request_headers()
    assert expected_body_json == slicer.request_body_json()
    assert expected_body_data == slicer.request_body_data()

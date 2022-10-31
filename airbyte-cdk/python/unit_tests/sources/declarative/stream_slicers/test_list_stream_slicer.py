#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer

slice_values = ["customer", "store", "subscription"]
cursor_field = "owner_resource"
options = {"cursor_field": "owner_resource"}


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
        (
            "test_using_cursor_from_options",
            '["customer", "store", "subscription"]',
            "{{ options['cursor_field'] }}",
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
    ],
)
def test_list_stream_slicer(test_name, slice_values, cursor_field, expected_slices):
    slicer = ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, options=options)
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
    slicer = ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, options={})
    if expected_state:
        slicer.update_cursor(stream_slice, last_record)
        updated_state = slicer.get_stream_state()
        assert expected_state == updated_state
    else:
        with pytest.raises(ValueError):
            slicer.update_cursor(stream_slice, last_record)


@pytest.mark.parametrize(
    "test_name, request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            "test_inject_into_req_param",
            RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="owner_resource"),
            {"owner_resource": "customer"},
            {},
            {},
            {},
        ),
        (
            "test_pass_by_header",
            RequestOption(inject_into=RequestOptionType.header, options={}, field_name="owner_resource"),
            {},
            {"owner_resource": "customer"},
            {},
            {},
        ),
        (
            "test_inject_into_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, options={}, field_name="owner_resource"),
            {},
            {},
            {"owner_resource": "customer"},
            {},
        ),
        (
            "test_inject_into_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, options={}, field_name="owner_resource"),
            {},
            {},
            {},
            {"owner_resource": "customer"},
        ),
        (
            "test_inject_into_path",
            RequestOption(RequestOptionType.path, {}),
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
            ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, request_option=request_option, options={})
            assert False
        except ValueError:
            return
    slicer = ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, request_option=request_option, options={})
    stream_slice = {cursor_field: "customer"}

    assert expected_req_params == slicer.get_request_params(stream_slice=stream_slice)
    assert expected_headers == slicer.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == slicer.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == slicer.get_request_body_data(stream_slice=stream_slice)


def test_request_option_before_updating_cursor():
    request_option = RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="owner_resource")
    if request_option.inject_into == RequestOptionType.path:
        try:
            ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, request_option=request_option, options={})
            assert False
        except ValueError:
            return
    slicer = ListStreamSlicer(slice_values=slice_values, cursor_field=cursor_field, config={}, request_option=request_option, options={})
    stream_slice = {cursor_field: "customer"}

    assert {} == slicer.get_request_params(stream_slice)
    assert {} == slicer.get_request_headers()
    assert {} == slicer.get_request_body_json()
    assert {} == slicer.get_request_body_data()

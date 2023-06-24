#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType

partition_values = ["customer", "store", "subscription"]
cursor_field = "owner_resource"
parameters = {"cursor_field": "owner_resource"}


@pytest.mark.parametrize(
    "test_name, partition_values, cursor_field, expected_slices",
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
            "test_using_cursor_from_parameters",
            '["customer", "store", "subscription"]',
            "{{ parameters['cursor_field'] }}",
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
    ],
)
def test_list_partition_router(test_name, partition_values, cursor_field, expected_slices):
    slicer = ListPartitionRouter(values=partition_values, cursor_field=cursor_field, config={}, parameters=parameters)
    slices = [s for s in slicer.stream_slices()]
    assert slices == expected_slices


@pytest.mark.parametrize(
    "test_name, request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            "test_inject_into_req_param",
            RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner_resource"),
            {"owner_resource": "customer"},
            {},
            {},
            {},
        ),
        (
            "test_pass_by_header",
            RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="owner_resource"),
            {},
            {"owner_resource": "customer"},
            {},
            {},
        ),
        (
            "test_inject_into_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="owner_resource"),
            {},
            {},
            {"owner_resource": "customer"},
            {},
        ),
        (
            "test_inject_into_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="owner_resource"),
            {},
            {},
            {},
            {"owner_resource": "customer"},
        ),
    ],
)
def test_request_option(test_name, request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    partition_router = ListPartitionRouter(values=partition_values, cursor_field=cursor_field, config={}, request_option=request_option, parameters={})
    stream_slice = {cursor_field: "customer"}

    assert expected_req_params == partition_router.get_request_params(stream_slice=stream_slice)
    assert expected_headers == partition_router.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == partition_router.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == partition_router.get_request_body_data(stream_slice=stream_slice)


def test_request_option_before_updating_cursor():
    request_option = RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner_resource")
    partition_router = ListPartitionRouter(values=partition_values, cursor_field=cursor_field, config={}, request_option=request_option, parameters={})
    stream_slice = {cursor_field: "customer"}

    assert {} == partition_router.get_request_params(stream_slice)
    assert {} == partition_router.get_request_headers()
    assert {} == partition_router.get_request_body_json()
    assert {} == partition_router.get_request_body_data()

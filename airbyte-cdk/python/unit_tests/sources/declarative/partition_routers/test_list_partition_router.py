#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.types import StreamSlice

partition_values = ["customer", "store", "subscription"]
cursor_field = "owner_resource"
parameters = {"cursor_field": "owner_resource"}


@pytest.mark.parametrize(
    "partition_values, cursor_field, expected_slices",
    [
        (
            ["customer", "store", "subscription"],
            "owner_resource",
            [
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={}),
            ],
        ),
        (
            '["customer", "store", "subscription"]',
            "owner_resource",
            [
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={}),
            ],
        ),
        (
            '["customer", "store", "subscription"]',
            "{{ parameters['cursor_field'] }}",
            [
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={}),
            ],
        ),
    ],
    ids=[
        "test_single_element",
        "test_input_list_is_string",
        "test_using_cursor_from_parameters",
    ],
)
def test_list_partition_router(partition_values, cursor_field, expected_slices):
    slicer = ListPartitionRouter(values=partition_values, cursor_field=cursor_field, config={}, parameters=parameters)
    slices = [s for s in slicer.stream_slices()]
    assert slices == expected_slices
    assert all(isinstance(s, StreamSlice) for s in slices)


@pytest.mark.parametrize(
    "request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner_resource"),
            {"owner_resource": "customer"},
            {},
            {},
            {},
        ),
        (
            RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="owner_resource"),
            {},
            {"owner_resource": "customer"},
            {},
            {},
        ),
        (
            RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="owner_resource"),
            {},
            {},
            {"owner_resource": "customer"},
            {},
        ),
        (
            RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="owner_resource"),
            {},
            {},
            {},
            {"owner_resource": "customer"},
        ),
    ],
    ids=[
        "test_inject_into_req_param",
        "test_pass_by_header",
        "test_inject_into_body_json",
        "test_inject_into_body_data",
    ],
)
def test_request_option(request_option, expected_req_params, expected_headers, expected_body_json, expected_body_data):
    partition_router = ListPartitionRouter(
        values=partition_values, cursor_field=cursor_field, config={}, request_option=request_option, parameters={}
    )
    stream_slice = {cursor_field: "customer"}

    assert partition_router.get_request_params(stream_slice=stream_slice) == expected_req_params
    assert partition_router.get_request_headers(stream_slice=stream_slice) == expected_headers
    assert partition_router.get_request_body_json(stream_slice=stream_slice) == expected_body_json
    assert partition_router.get_request_body_data(stream_slice=stream_slice) == expected_body_data


@pytest.mark.parametrize(
    "stream_slice",
    [
        pytest.param({}, id="test_request_option_is_empty_if_empty_stream_slice"),
        pytest.param({"not the cursor": "value"}, id="test_request_option_is_empty_if_the_stream_slice_does_not_have_cursor_field"),
        pytest.param(None, id="test_request_option_is_empty_if_no_stream_slice"),
    ],
)
def test_request_option_is_empty_if_no_stream_slice(stream_slice):
    request_option = RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="owner_resource")
    partition_router = ListPartitionRouter(
        values=partition_values, cursor_field=cursor_field, config={}, request_option=request_option, parameters={}
    )
    assert {} == partition_router.get_request_body_data(stream_slice=stream_slice)


@pytest.mark.parametrize(
    "field_name_interpolation, expected_request_params",
    [
        ("{{parameters['partition_name']}}", {"parameters_partition": "customer"}),
        ("{{config['partition_name']}}", {"config_partition": "customer"}),
    ],
    ids=[
        "parameters_interpolation",
        "config_interpolation",
    ],
)
def test_request_options_interpolation(field_name_interpolation: str, expected_request_params: dict):
    config = {"partition_name": "config_partition"}
    parameters = {"partition_name": "parameters_partition"}
    request_option = RequestOption(
        inject_into=RequestOptionType.request_parameter, parameters=parameters, field_name=field_name_interpolation
    )
    partition_router = ListPartitionRouter(
        values=partition_values, cursor_field=cursor_field, config=config, request_option=request_option, parameters=parameters
    )
    stream_slice = {cursor_field: "customer"}

    assert partition_router.get_request_params(stream_slice=stream_slice) == expected_request_params


def test_request_option_before_updating_cursor():
    request_option = RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner_resource")
    partition_router = ListPartitionRouter(
        values=partition_values, cursor_field=cursor_field, config={}, request_option=request_option, parameters={}
    )
    stream_slice = {cursor_field: "customer"}

    assert {} == partition_router.get_request_params(stream_slice)
    assert {} == partition_router.get_request_headers()
    assert {} == partition_router.get_request_body_json()
    assert {} == partition_router.get_request_body_data()

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import CartesianProductStreamSlicer, ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.types import StreamSlice


@pytest.mark.parametrize(
    "test_name, stream_slicers, expected_slices",
    [
        (
            "test_single_stream_slicer",
            [ListPartitionRouter(values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, parameters={})],
            [StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={}),
             StreamSlice(partition={"owner_resource": "store"}, cursor_slice={}),
             StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={})],
        ),
        (
            "test_two_stream_slicers",
            [
                ListPartitionRouter(values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, parameters={}),
                ListPartitionRouter(values=["A", "B"], cursor_field="letter", config={}, parameters={}),
            ],
            [
                StreamSlice(partition={"owner_resource": "customer", "letter": "A"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "customer", "letter": "B"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "store", "letter": "A"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "store", "letter": "B"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "subscription", "letter": "A"}, cursor_slice={}),
                StreamSlice(partition={"owner_resource": "subscription", "letter": "B"}, cursor_slice={}),
            ],
        ),
        (
                "test_singledatetime",
                [
                    DatetimeBasedCursor(
                        start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
                        end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", parameters={}),
                        step="P1D",
                        cursor_field=InterpolatedString.create("", parameters={}),
                        datetime_format="%Y-%m-%d",
                        cursor_granularity="P1D",
                        config={},
                        parameters={},
                    ),
                ],
                [
                    StreamSlice(partition={}, cursor_slice={"start_time": "2021-01-01", "end_time": "2021-01-01"}),
                    StreamSlice(partition={}, cursor_slice={"start_time": "2021-01-02", "end_time": "2021-01-02"}),
                    StreamSlice(partition={}, cursor_slice={"start_time": "2021-01-03", "end_time": "2021-01-03"}),
                ],
        ),
        (
            "test_list_and_datetime",
            [
                ListPartitionRouter(values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, parameters={}),
                DatetimeBasedCursor(
                    start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
                    end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", parameters={}),
                    step="P1D",
                    cursor_field=InterpolatedString.create("", parameters={}),
                    datetime_format="%Y-%m-%d",
                    cursor_granularity="P1D",
                    config={},
                    parameters={},
                ),
            ],
            [
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={"start_time": "2021-01-01", "end_time": "2021-01-01"}),
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={"start_time": "2021-01-02", "end_time": "2021-01-02"}),
                StreamSlice(partition={"owner_resource": "customer"}, cursor_slice={"start_time": "2021-01-03", "end_time": "2021-01-03"}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={"start_time": "2021-01-01", "end_time": "2021-01-01"}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={"start_time": "2021-01-02", "end_time": "2021-01-02"}),
                StreamSlice(partition={"owner_resource": "store"}, cursor_slice={"start_time": "2021-01-03", "end_time": "2021-01-03"}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={"start_time": "2021-01-01", "end_time": "2021-01-01"}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={"start_time": "2021-01-02", "end_time": "2021-01-02"}),
                StreamSlice(partition={"owner_resource": "subscription"}, cursor_slice={"start_time": "2021-01-03", "end_time": "2021-01-03"}),
            ],
        ),
    ],
)
def test_substream_slicer(test_name, stream_slicers, expected_slices):
    slicer = CartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    slices = [s for s in slicer.stream_slices()]
    assert slices == expected_slices


def test_stream_slices_raises_exception_if_multiple_cursor_slice_components():
    stream_slicers = [
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", parameters={}),
            step="P1D",
            cursor_field=InterpolatedString.create("", parameters={}),
            datetime_format="%Y-%m-%d",
            cursor_granularity="P1D",
            config={},
            parameters={},
        ),
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", parameters={}),
            step="P1D",
            cursor_field=InterpolatedString.create("", parameters={}),
            datetime_format="%Y-%m-%d",
            cursor_granularity="P1D",
            config={},
            parameters={},
        ),
    ]
    slicer = CartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    with pytest.raises(ValueError):
        list(slicer.stream_slices())


@pytest.mark.parametrize(
    "test_name, stream_1_request_option, stream_2_request_option, expected_req_params, expected_headers,expected_body_json, expected_body_data",
    [
        (
            "test_param_header",
            RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="repo"),
            {"owner": "customer"},
            {"repo": "airbyte"},
            {},
            {},
        ),
        (
            "test_header_header",
            RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="repo"),
            {},
            {"owner": "customer", "repo": "airbyte"},
            {},
            {},
        ),
        (
            "test_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="repo"),
            {},
            {},
            {},
            {"owner": "customer", "repo": "airbyte"},
        ),
        (
            "test_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="repo"),
            {},
            {},
            {"owner": "customer", "repo": "airbyte"},
            {},
        ),
    ],
)
def test_request_option(
    test_name,
    stream_1_request_option,
    stream_2_request_option,
    expected_req_params,
    expected_headers,
    expected_body_json,
    expected_body_data,
):
    slicer = CartesianProductStreamSlicer(
        stream_slicers=[
            ListPartitionRouter(
                values=["customer", "store", "subscription"],
                cursor_field="owner_resource",
                config={},
                request_option=stream_1_request_option,
                parameters={},
            ),
            ListPartitionRouter(
                values=["airbyte", "airbyte-cloud"],
                cursor_field="repository",
                config={},
                request_option=stream_2_request_option,
                parameters={},
            ),
        ],
        parameters={},
    )
    stream_slice = {"owner_resource": "customer", "repository": "airbyte"}

    assert slicer.get_request_params(stream_slice=stream_slice) == expected_req_params
    assert slicer.get_request_headers(stream_slice=stream_slice) == expected_headers
    assert slicer.get_request_body_json(stream_slice=stream_slice) == expected_body_json
    assert slicer.get_request_body_data(stream_slice=stream_slice) == expected_body_data


def test_request_option_before_updating_cursor():
    stream_1_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="owner")
    stream_2_request_option = RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="repo")
    slicer = CartesianProductStreamSlicer(
        stream_slicers=[
            ListPartitionRouter(
                values=["customer", "store", "subscription"],
                cursor_field="owner_resource",
                config={},
                request_option=stream_1_request_option,
                parameters={},
            ),
            ListPartitionRouter(
                values=["airbyte", "airbyte-cloud"],
                cursor_field="repository",
                config={},
                request_option=stream_2_request_option,
                parameters={},
            ),
        ],
        parameters={},
    )
    assert {} == slicer.get_request_params()
    assert {} == slicer.get_request_headers()
    assert {} == slicer.get_request_body_json()
    assert {} == slicer.get_request_body_data()

#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer


@pytest.mark.parametrize(
    "test_name, stream_slicers, expected_slices",
    [
        (
            "test_single_stream_slicer",
            [ListStreamSlicer(slice_values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, options={})],
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
        (
            "test_two_stream_slicers",
            [
                ListStreamSlicer(slice_values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, options={}),
                ListStreamSlicer(slice_values=["A", "B"], cursor_field="letter", config={}, options={}),
            ],
            [
                {"owner_resource": "customer", "letter": "A"},
                {"owner_resource": "customer", "letter": "B"},
                {"owner_resource": "store", "letter": "A"},
                {"owner_resource": "store", "letter": "B"},
                {"owner_resource": "subscription", "letter": "A"},
                {"owner_resource": "subscription", "letter": "B"},
            ],
        ),
        (
            "test_list_and_datetime",
            [
                ListStreamSlicer(slice_values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, options={}),
                DatetimeStreamSlicer(
                    start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", options={}),
                    end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", options={}),
                    step="P1D",
                    cursor_field=InterpolatedString.create("", options={}),
                    datetime_format="%Y-%m-%d",
                    cursor_granularity="P1D",
                    config={},
                    options={},
                ),
            ],
            [
                {"owner_resource": "customer", "start_time": "2021-01-01", "end_time": "2021-01-01"},
                {"owner_resource": "customer", "start_time": "2021-01-02", "end_time": "2021-01-02"},
                {"owner_resource": "customer", "start_time": "2021-01-03", "end_time": "2021-01-03"},
                {"owner_resource": "store", "start_time": "2021-01-01", "end_time": "2021-01-01"},
                {"owner_resource": "store", "start_time": "2021-01-02", "end_time": "2021-01-02"},
                {"owner_resource": "store", "start_time": "2021-01-03", "end_time": "2021-01-03"},
                {"owner_resource": "subscription", "start_time": "2021-01-01", "end_time": "2021-01-01"},
                {"owner_resource": "subscription", "start_time": "2021-01-02", "end_time": "2021-01-02"},
                {"owner_resource": "subscription", "start_time": "2021-01-03", "end_time": "2021-01-03"},
            ],
        ),
    ],
)
def test_substream_slicer(test_name, stream_slicers, expected_slices):
    slicer = CartesianProductStreamSlicer(stream_slicers=stream_slicers, options={})
    slices = [s for s in slicer.stream_slices(SyncMode.incremental, stream_state=None)]
    assert slices == expected_slices


@pytest.mark.parametrize(
    "test_name, stream_slice, expected_state",
    [
        ("test_update_cursor_no_state_no_record", {}, {}),
        ("test_update_cursor_partial_state", {"owner_resource": "customer"}, {"owner_resource": "customer"}),
        (
            "test_update_cursor_full_state",
            {"owner_resource": "customer", "date": "2021-01-01"},
            {"owner_resource": "customer", "date": "2021-01-01"},
        ),
    ],
)
def test_update_cursor(test_name, stream_slice, expected_state):
    stream_slicers = [
        ListStreamSlicer(slice_values=["customer", "store", "subscription"], cursor_field="owner_resource", config={}, options={}),
        DatetimeStreamSlicer(
            start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", options={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-03", datetime_format="%Y-%m-%d", options={}),
            step="P1D",
            cursor_field=InterpolatedString(string="date", options={}),
            datetime_format="%Y-%m-%d",
            cursor_granularity="P1D",
            config={},
            options={},
        ),
    ]
    slicer = CartesianProductStreamSlicer(stream_slicers=stream_slicers, options={})

    if expected_state:
        slicer.update_cursor(stream_slice, None)
        updated_state = slicer.get_stream_state()
        assert expected_state == updated_state
    else:
        with pytest.raises(ValueError):
            slicer.update_cursor(stream_slice, None)


@pytest.mark.parametrize(
    "test_name, stream_1_request_option, stream_2_request_option, expected_req_params, expected_headers,expected_body_json, expected_body_data",
    [
        (
            "test_param_header",
            RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.header, options={}, field_name="repo"),
            {"owner": "customer"},
            {"repo": "airbyte"},
            {},
            {},
        ),
        (
            "test_header_header",
            RequestOption(inject_into=RequestOptionType.header, options={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.header, options={}, field_name="repo"),
            {},
            {"owner": "customer", "repo": "airbyte"},
            {},
            {},
        ),
        (
            "test_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, options={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.body_data, options={}, field_name="repo"),
            {},
            {},
            {},
            {"owner": "customer", "repo": "airbyte"},
        ),
        (
            "test_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, options={}, field_name="owner"),
            RequestOption(inject_into=RequestOptionType.body_json, options={}, field_name="repo"),
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
            ListStreamSlicer(
                slice_values=["customer", "store", "subscription"],
                cursor_field="owner_resource",
                config={},
                request_option=stream_1_request_option,
                options={},
            ),
            ListStreamSlicer(
                slice_values=["airbyte", "airbyte-cloud"],
                cursor_field="repository",
                config={},
                request_option=stream_2_request_option,
                options={},
            ),
        ],
        options={},
    )
    stream_slice = {"owner_resource": "customer", "repository": "airbyte"}

    assert expected_req_params == slicer.get_request_params(stream_slice=stream_slice)
    assert expected_headers == slicer.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == slicer.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == slicer.get_request_body_data(stream_slice=stream_slice)


def test_request_option_before_updating_cursor():
    stream_1_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="owner")
    stream_2_request_option = RequestOption(inject_into=RequestOptionType.header, options={}, field_name="repo")
    slicer = CartesianProductStreamSlicer(
        stream_slicers=[
            ListStreamSlicer(
                slice_values=["customer", "store", "subscription"],
                cursor_field="owner_resource",
                config={},
                request_option=stream_1_request_option,
                options={},
            ),
            ListStreamSlicer(
                slice_values=["airbyte", "airbyte-cloud"],
                cursor_field="repository",
                config={},
                request_option=stream_2_request_option,
                options={},
            ),
        ],
        options={},
    )
    assert {} == slicer.get_request_params()
    assert {} == slicer.get_request_headers()
    assert {} == slicer.get_request_body_json()
    assert {} == slicer.get_request_body_data()

#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import DatetimeBasedRequestOptionsProvider
from airbyte_cdk.sources.declarative.types import StreamSlice


@pytest.mark.parametrize(
    "start_time_option, end_time_option, partition_field_start, partition_field_end, stream_slice, expected_request_options",
    [
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.request_parameter, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.request_parameter, parameters={}),
            "custom_start",
            "custom_end",
            StreamSlice(cursor_slice={"custom_start": "2024-06-01", "custom_end": "2024-06-02"}, partition={}),
            {"after": "2024-06-01", "before": "2024-06-02"},
            id="test_request_params",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.request_parameter, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.request_parameter, parameters={}),
            None,
            None,
            StreamSlice(cursor_slice={"start_time": "2024-06-01", "end_time": "2024-06-02"}, partition={}),
            {"after": "2024-06-01", "before": "2024-06-02"},
            id="test_request_params_with_default_partition_fields",
        ),
        pytest.param(
            None,
            RequestOption(field_name="before", inject_into=RequestOptionType.request_parameter, parameters={}),
            None,
            None,
            StreamSlice(cursor_slice={"start_time": "2024-06-01", "end_time": "2024-06-02"}, partition={}),
            {"before": "2024-06-02"},
            id="test_request_params_no_start_time_option",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.request_parameter, parameters={}),
            None,
            None,
            None,
            StreamSlice(cursor_slice={"start_time": "2024-06-01", "end_time": "2024-06-02"}, partition={}),
            {"after": "2024-06-01"},
            id="test_request_params_no_end_time_option",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.request_parameter, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.request_parameter, parameters={}),
            None,
            None,
            None,
            {},
            id="test_request_params_no_slice",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.header, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.header, parameters={}),
            "custom_start",
            "custom_end",
            StreamSlice(cursor_slice={"custom_start": "2024-06-01", "custom_end": "2024-06-02"}, partition={}),
            {"after": "2024-06-01", "before": "2024-06-02"},
            id="test_request_headers",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.body_data, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.body_data, parameters={}),
            "custom_start",
            "custom_end",
            StreamSlice(cursor_slice={"custom_start": "2024-06-01", "custom_end": "2024-06-02"}, partition={}),
            {"after": "2024-06-01", "before": "2024-06-02"},
            id="test_request_request_body_data",
        ),
        pytest.param(
            RequestOption(field_name="after", inject_into=RequestOptionType.body_json, parameters={}),
            RequestOption(field_name="before", inject_into=RequestOptionType.body_json, parameters={}),
            "custom_start",
            "custom_end",
            StreamSlice(cursor_slice={"custom_start": "2024-06-01", "custom_end": "2024-06-02"}, partition={}),
            {"after": "2024-06-01", "before": "2024-06-02"},
            id="test_request_request_body_json",
        ),
    ],
)
def test_datetime_based_request_options_provider(
        start_time_option,
        end_time_option,
        partition_field_start,
        partition_field_end,
        stream_slice,
        expected_request_options
):
    config = {}
    request_options_provider = DatetimeBasedRequestOptionsProvider(
        start_time_option=start_time_option,
        end_time_option=end_time_option,
        partition_field_start=partition_field_start,
        partition_field_end=partition_field_end,
        config=config,
        parameters={}
    )

    request_option_type = start_time_option.inject_into if isinstance(start_time_option, RequestOption) else None
    match request_option_type:
        case RequestOptionType.request_parameter:
            actual_request_options = request_options_provider.get_request_params(stream_slice=stream_slice)
        case RequestOptionType.header:
            actual_request_options = request_options_provider.get_request_headers(stream_slice=stream_slice)
        case RequestOptionType.body_data:
            actual_request_options = request_options_provider.get_request_body_data(stream_slice=stream_slice)
        case RequestOptionType.body_json:
            actual_request_options = request_options_provider.get_request_body_json(stream_slice=stream_slice)
        case _:
            # We defer to testing the default RequestOptions using get_request_params()
            actual_request_options = request_options_provider.get_request_params(stream_slice=stream_slice)

    assert actual_request_options == expected_request_options

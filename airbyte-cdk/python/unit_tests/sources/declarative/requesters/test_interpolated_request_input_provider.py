#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.interpolated_request_input_provider import InterpolatedRequestInputProvider


@pytest.mark.parametrize(
    "test_name, input_request_data, expected_request_data",
    [
        ("test_static_string_data", "a_static_value", "a_static_value"),
        ("test_string_depends_on_state", "key={{ stream_state['state_key'] }}", "key=state_value"),
        ("test_string_depends_on_next_page_token", "{{ next_page_token['token_key'] }} + ultra", "token_value + ultra"),
    ],
)
def test_interpolated_string_request_input_provider(test_name, input_request_data, expected_request_data):
    config = {"config_key": "value_of_config"}
    stream_state = {"state_key": "state_value"}
    next_page_token = {"token_key": "token_value"}

    provider = InterpolatedRequestInputProvider(config=config, request_inputs=input_request_data)
    actual_request_data = provider.request_inputs(stream_state=stream_state, next_page_token=next_page_token)

    assert isinstance(provider._interpolator, InterpolatedString)
    assert actual_request_data == expected_request_data


@pytest.mark.parametrize(
    "test_name, input_request_data, expected_request_data",
    [
        ("test_static_map_data", {"a_static_request_param": "a_static_value"}, {"a_static_request_param": "a_static_value"}),
        ("test_map_depends_on_stream_slice", {"read_from_slice": "{{ stream_slice['slice_key'] }}"}, {"read_from_slice": "slice_value"}),
        ("test_map_depends_on_config", {"read_from_config": "{{ config['config_key'] }}"}, {"read_from_config": "value_of_config"}),
        ("test_defaults_to_empty_dictionary", None, {}),
    ],
)
def test_initialize_interpolated_mapping_request_input_provider(test_name, input_request_data, expected_request_data):
    config = {"config_key": "value_of_config"}
    stream_slice = {"slice_key": "slice_value"}

    provider = InterpolatedRequestInputProvider(config=config, request_inputs=input_request_data)
    actual_request_data = provider.request_inputs(stream_state={}, stream_slice=stream_slice)

    assert isinstance(provider._interpolator, InterpolatedMapping)
    assert actual_request_data == expected_request_data

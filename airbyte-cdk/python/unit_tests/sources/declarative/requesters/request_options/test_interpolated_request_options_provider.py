#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)

state = {"date": "2021-01-01"}
stream_slice = {"start_date": "2020-01-01"}
next_page_token = {"offset": 12345, "page": 27}
config = {"option": "OPTION"}


@pytest.mark.parametrize(
    "test_name, input_request_params, expected_request_params",
    [
        ("test_static_param", {"a_static_request_param": "a_static_value"}, {"a_static_request_param": "a_static_value"}),
        ("test_value_depends_on_state", {"read_from_state": "{{ stream_state['date'] }}"}, {"read_from_state": "2021-01-01"}),
        ("test_value_depends_on_stream_slice", {"read_from_slice": "{{ stream_slice['start_date'] }}"}, {"read_from_slice": "2020-01-01"}),
        ("test_value_depends_on_next_page_token", {"read_from_token": "{{ next_page_token['offset'] }}"}, {"read_from_token": "12345"}),
        ("test_value_depends_on_config", {"read_from_config": "{{ config['option'] }}"}, {"read_from_config": "OPTION"}),
        (
            "test_parameter_is_interpolated",
            {"{{ stream_state['date'] }} - {{stream_slice['start_date']}} - {{next_page_token['offset']}} - {{config['option']}}": "ABC"},
            {"2021-01-01 - 2020-01-01 - 12345 - OPTION": "ABC"},
        ),
        ("test_boolean_false_value", {"boolean_false": "{{ False }}"}, {"boolean_false": "False"}),
        ("test_integer_falsy_value", {"integer_falsy": "{{ 0 }}"}, {"integer_falsy": "0"}),
        ("test_number_falsy_value", {"number_falsy": "{{ 0.0 }}"}, {"number_falsy": "0.0"}),
        ("test_string_falsy_value", {"string_falsy": "{{ '' }}"}, {}),
        ("test_none_value", {"none_value": "{{ None }}"}, {"none_value": "None"}),
    ],
)
def test_interpolated_request_params(test_name, input_request_params, expected_request_params):
    provider = InterpolatedRequestOptionsProvider(config=config, request_parameters=input_request_params, parameters={})

    actual_request_params = provider.get_request_params(stream_state=state, stream_slice=stream_slice, next_page_token=next_page_token)

    assert actual_request_params == expected_request_params


@pytest.mark.parametrize(
    "test_name, input_request_json, expected_request_json",
    [
        ("test_static_json", {"a_static_request_param": "a_static_value"}, {"a_static_request_param": "a_static_value"}),
        ("test_value_depends_on_state", {"read_from_state": "{{ stream_state['date'] }}"}, {"read_from_state": "2021-01-01"}),
        ("test_value_depends_on_stream_slice", {"read_from_slice": "{{ stream_slice['start_date'] }}"}, {"read_from_slice": "2020-01-01"}),
        ("test_value_depends_on_next_page_token", {"read_from_token": "{{ next_page_token['offset'] }}"}, {"read_from_token": 12345}),
        ("test_value_depends_on_config", {"read_from_config": "{{ config['option'] }}"}, {"read_from_config": "OPTION"}),
        (
            "test_interpolated_keys",
            {"{{ stream_state['date'] }}": 123, "{{ config['option'] }}": "ABC"},
            {"2021-01-01": 123, "OPTION": "ABC"},
        ),
        ("test_boolean_false_value", {"boolean_false": "{{ False }}"}, {"boolean_false": False}),
        ("test_integer_falsy_value", {"integer_falsy": "{{ 0 }}"}, {"integer_falsy": 0}),
        ("test_number_falsy_value", {"number_falsy": "{{ 0.0 }}"}, {"number_falsy": 0.0}),
        ("test_string_falsy_value", {"string_falsy": "{{ '' }}"}, {}),
        ("test_none_value", {"none_value": "{{ None }}"}, {}),
        ("test_string", """{"nested": { "key": "{{ config['option'] }}" }}""", {"nested": {"key": "OPTION"}}),
        ("test_nested_objects", {"nested": {"key": "{{ config['option'] }}"}}, {"nested": {"key": "OPTION"}}),
        (
            "test_nested_objects_interpolated keys",
            {"nested": {"{{ stream_state['date'] }}": "{{ config['option'] }}"}},
            {"nested": {"2021-01-01": "OPTION"}},
        ),
    ],
)
def test_interpolated_request_json(test_name, input_request_json, expected_request_json):
    provider = InterpolatedRequestOptionsProvider(config=config, request_body_json=input_request_json, parameters={})

    actual_request_json = provider.get_request_body_json(stream_state=state, stream_slice=stream_slice, next_page_token=next_page_token)

    assert actual_request_json == expected_request_json


@pytest.mark.parametrize(
    "test_name, input_request_data, expected_request_data",
    [
        ("test_static_map_data", {"a_static_request_param": "a_static_value"}, {"a_static_request_param": "a_static_value"}),
        ("test_map_depends_on_stream_slice", {"read_from_slice": "{{ stream_slice['start_date'] }}"}, {"read_from_slice": "2020-01-01"}),
        ("test_map_depends_on_config", {"read_from_config": "{{ config['option'] }}"}, {"read_from_config": "OPTION"}),
        ("test_defaults_to_empty_dict", None, {}),
        ("test_interpolated_keys", {"{{ stream_state['date'] }} - {{ next_page_token['offset'] }}": "ABC"}, {"2021-01-01 - 12345": "ABC"}),
    ],
)
def test_interpolated_request_data(test_name, input_request_data, expected_request_data):
    provider = InterpolatedRequestOptionsProvider(config=config, request_body_data=input_request_data, parameters={})

    actual_request_data = provider.get_request_body_data(stream_state=state, stream_slice=stream_slice, next_page_token=next_page_token)

    assert actual_request_data == expected_request_data


def test_error_on_create_for_both_request_json_and_data():
    request_json = {"body_key": "{{ stream_slice['start_date'] }}"}
    request_data = "interpolate_me=5&invalid={{ config['option'] }}"
    with pytest.raises(ValueError):
        InterpolatedRequestOptionsProvider(config=config, request_body_json=request_json, request_body_data=request_data, parameters={})

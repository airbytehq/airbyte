#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.requesters.request_params.interpolated_request_parameter_provider import (
    InterpolatedRequestParameterProvider,
)

state = {"date": "2021-01-01"}
stream_slice = {"start_date": "2020-01-01"}
next_page_token = {"offset": "12345"}
config = {"option": "OPTION"}


def test():
    request_parameters = {"a_static_request_param": "a_static_value"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_parameters == request_params


def test_value_depends_on_state():
    request_parameters = {"a_static_request_param": "{{ stream_state['date'] }}"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_params["a_static_request_param"] == state["date"]


def test_value_depends_on_stream_slice():
    request_parameters = {"a_static_request_param": "{{ stream_slice['start_date'] }}"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_params["a_static_request_param"] == stream_slice["start_date"]


def test_value_depends_on_next_page_token():
    request_parameters = {"a_static_request_param": "{{ next_page_token['offset'] }}"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_params["a_static_request_param"] == next_page_token["offset"]


def test_value_depends_on_config():
    request_parameters = {"a_static_request_param": "{{ config['option'] }}"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_params["a_static_request_param"] == config["option"]


def test_parameter_is_interpolated():
    request_parameters = {
        "{{ stream_state['date'] }} - {{stream_slice['start_date']}} - {{next_page_token['offset']}} - {{config['option']}}": "ABC"
    }
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params(state, stream_slice, next_page_token)

    assert request_params[f"{state['date']} - {stream_slice['start_date']} - {next_page_token['offset']} - {config['option']}"] == "ABC"


def test_none_value():
    request_parameters = {"a_static_request_param": "{{ stream_state['date'] }}"}
    provider = InterpolatedRequestParameterProvider(request_parameters=request_parameters, config=config)

    request_params = provider.request_params({}, stream_slice, next_page_token)

    assert len(request_params) == 0

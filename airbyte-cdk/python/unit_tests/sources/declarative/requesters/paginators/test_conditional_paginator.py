#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator import InterpolatedConditionalPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)


@pytest.mark.parametrize(
    "test_name, stop_condition_template, pass_by, body_data, expected_next_page_token",
    [
        (
            "test_stop_pagination_from_response_body",
            "{{ not decoded_response['accounts'] }}",
            RequestOptionType.body_json,
            {"data": "data"},
            None,
        ),
        (
            "test_stop_pagination_from_config",
            "{{ config['response_override'] == decoded_response['_metadata']['content'] }}",
            RequestOptionType.body_json,
            {"data": "data"},
            None,
        ),
        (
            "test_continue_pagination_from_response_body",
            "{{ decoded_response['end'] == decoded_response['total'] - 1 }}",
            RequestOptionType.body_json,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_response_headers",
            "{{ decoded_response['headers']['has_more'] }}",
            RequestOptionType.body_json,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_last_records_body_json",
            "{{ last_records[-1]['more_records'] == False }}",
            RequestOptionType.body_json,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_last_records_body_data",
            "{{ last_records[-1]['more_records'] == False }}",
            RequestOptionType.body_data,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_last_records_params",
            "{{ last_records[-1]['more_records'] == False }}",
            RequestOptionType.request_parameter,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_last_records_header",
            "{{ last_records[-1]['more_records'] == False }}",
            RequestOptionType.header,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_from_last_records_path",
            "{{ last_records[-1]['more_records'] == False }}",
            RequestOptionType.path,
            {"data": "data"},
            {"next_page_token": 99},
        ),
        (
            "test_continue_pagination_for_empty_dict_evaluates_false",
            "{{ decoded_response['characters'] }}",
            RequestOptionType.body_json,
            {"data": "data"},
            {"next_page_token": 99},
        ),
    ],
)
def test_interpolated_conditional_paginator(test_name, stop_condition_template, pass_by, body_data, expected_next_page_token):
    decoder = JsonDecoder()
    config = {"response_override": "stop_if_you_see_me"}

    cursor_value = "{{ decoded_response.end }}"
    strategy = CursorPaginationStrategy(cursor_value, decoder=decoder, config=config)
    url_base = "https://airbyte.io"

    pass_by_to_kwargs = {
        RequestOptionType.request_parameter: {"param": "param"},
        RequestOptionType.header: {"header": "header"},
        RequestOptionType.body_data: body_data,
    }

    request_options_provider = InterpolatedRequestOptionsProvider(
        config=config,
        request_headers=pass_by_to_kwargs.get(RequestOptionType.header),
        request_parameters=pass_by_to_kwargs.get(RequestOptionType.request_parameter),
        request_body_data=pass_by_to_kwargs.get(RequestOptionType.body_data),
    )
    if pass_by == RequestOptionType.path:
        page_token = RequestOption(pass_by)
    else:
        page_token = RequestOption(inject_into=pass_by, field_name="from")
    response = requests.Response()
    response.headers = {"has_more": True}
    response_body = {"_metadata": {"content": "stop_if_you_see_me"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    paginator = InterpolatedConditionalPaginator(
        InterpolatedBoolean(stop_condition_template), request_options_provider, page_token, strategy, config, url_base, decoder
    )
    next_page_token = paginator.next_page_token(response, last_records)

    pass_by_to_mapping = {
        RequestOptionType.request_parameter: paginator.request_params(),
        RequestOptionType.header: paginator.request_headers(),
        RequestOptionType.path: paginator.path(),
        RequestOptionType.body_json: paginator.request_body_json(),
        RequestOptionType.body_data: paginator.request_body_data(),
    }

    assert next_page_token == expected_next_page_token
    for option_type, mapping in pass_by_to_mapping.items():
        if option_type == pass_by and expected_next_page_token:
            if isinstance(body_data, str) and pass_by == RequestOptionType.body_data:
                assert mapping == "from=99&data=data"
            elif option_type == RequestOptionType.path:
                assert mapping == "99"
            else:
                assert mapping == {**{"from": 99}, **pass_by_to_kwargs.get(option_type, {})}
        else:
            if option_type == RequestOptionType.path:
                assert mapping is None
            else:
                assert mapping == pass_by_to_kwargs.get(option_type, {})

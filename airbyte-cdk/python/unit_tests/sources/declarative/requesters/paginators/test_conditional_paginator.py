#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator import InterpolatedConditionalPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)


@pytest.mark.parametrize(
    "test_name, stop_condition_template, expected_next_page_token",
    [
        ("test_stop_pagination_from_response_body", "{{ not decoded_response['accounts'] }}", None),
        ("test_stop_pagination_from_config", "{{ config['response_override'] == decoded_response['_metadata']['content'] }}", None),
        (
            "test_continue_pagination_from_response_body",
            "{{ decoded_response['end'] == decoded_response['total'] - 1 }}",
            {"next_page_token": 99},
        ),
        ("test_continue_pagination_from_response_headers", "{{ decoded_response['headers']['has_more'] }}", {"next_page_token": 99}),
        ("test_continue_pagination_from_last_records", "{{ last_records[-1]['more_records'] == False }}", {"next_page_token": 99}),
        ("test_continue_pagination_for_empty_dict_evaluates_false", "{{ decoded_response['characters'] }}", {"next_page_token": 99}),
    ],
)
def test_interpolated_conditional_paginator(test_name, stop_condition_template, expected_next_page_token):
    decoder = JsonDecoder()
    config = {"response_override": "stop_if_you_see_me"}

    cursor_value = "{{ decoded_response.end }}"
    strategy = CursorPaginationStrategy(cursor_value, decoder=decoder, config=config)

    request_options_provider = InterpolatedRequestOptionsProvider(config=config)
    page_token = RequestOption(option_type=RequestOptionType.body_json, field_name="from")
    response = requests.Response()
    response.headers = {"has_more": True}
    response_body = {"_metadata": {"content": "stop_if_you_see_me"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    paginator = InterpolatedConditionalPaginator(
        InterpolatedBoolean(stop_condition_template), request_options_provider, page_token, strategy, config, None, decoder
    )
    next_page_token = paginator.next_page_token(response, last_records)

    assert next_page_token == expected_next_page_token

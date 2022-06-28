#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator

config = {"option": "OPTION"}

response = requests.Response()
response.headers = {"A_HEADER": "HEADER_VALUE"}
response_body = {"next_page_cursor": "12345"}
response._content = json.dumps(response_body).encode("utf-8")
last_responses = [{"id": 0}]
decoder = JsonDecoder()


@pytest.mark.parametrize(
    "test_name, next_page_token_template, expected_next_page_token",
    [
        ("test_value_is_static", {"cursor": "a_static_value"}, {"cursor": "a_static_value"}),
        (
            "test_value_depends_response_body",
            {"cursor": "{{ decoded_response['next_page_cursor'] }}"},
            {"cursor": response_body["next_page_cursor"]},
        ),
        ("test_value_depends_response_header", {"cursor": "{{ headers['A_HEADER'] }}"}, {"cursor": response.headers["A_HEADER"]}),
        ("test_value_depends_on_last_responses", {"cursor": "{{ last_records[-1]['id'] }}"}, {"cursor": "0"}),
        (
            "test_name_is_interpolated",
            {"{{ decoded_response['next_page_cursor'] }}": "a_static_value"},
            {response_body["next_page_cursor"]: "a_static_value"},
        ),
        ("test_token_is_none_if_field_not_found", {"cursor": "{{ decoded_response['not_next_page_cursor'] }}"}, None),
    ],
)
def test_interpolated_paginator(test_name, next_page_token_template, expected_next_page_token):
    paginator = InterpolatedPaginator(next_page_token_template=next_page_token_template, decoder=decoder, config=config)

    actual_next_page_token = paginator.next_page_token(response, last_responses)

    assert expected_next_page_token == actual_next_page_token

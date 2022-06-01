#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.requesters.paginators.conditional_paginator import ConditionalPaginator
from airbyte_cdk.sources.declarative.states.dict_state import DictState


@pytest.mark.parametrize(
    "test_name, stop_condition_template, expected_next_page_token, expected_page",
    [
        ("test_stop_pagination_from_response_body", "{{ not decoded_response['accounts'] }}", None, 1),
        ("test_stop_pagination_from_config", "{{ config['response_override'] == decoded_response['_metadata']['content'] }}", None, 1),
        ("test_continue_pagination_from_response_body", "{{ decoded_response['end'] == decoded_response['total'] - 1 }}", {"page": 2}, 2),
        ("test_continue_pagination_from_response_headers", "{{ decoded_response['headers']['has_more'] }}", {"page": 2}, 2),
        ("test_continue_pagination_from_last_records", "{{ last_records[-1]['more_records'] == False }}", {"page": 2}, 2),
        ("test_continue_pagination_for_empty_dict_evaluates_false", "{{ decoded_response['characters'] }}", {"page": 2}, 2),
    ],
)
def test_interpolated_request_header(test_name, stop_condition_template, expected_next_page_token, expected_page):
    state = DictState()
    state.update_state(page=1)
    decoder = JsonDecoder()
    config = {"response_override": "stop_if_you_see_me"}

    response = requests.Response()
    response.headers = {"has_more": True}
    response_body = {"_metadata": {"content": "stop_if_you_see_me"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    paginator = ConditionalPaginator(stop_condition_template, state, decoder, config)
    next_page_token = paginator.next_page_token(response, last_records)

    assert next_page_token == expected_next_page_token
    assert state.get_state("page") == expected_page

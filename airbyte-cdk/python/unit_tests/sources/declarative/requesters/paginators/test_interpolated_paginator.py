#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

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


def test_value_is_static():
    next_page_tokens = {"cursor": "a_static_value"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"cursor": "a_static_value"}


def test_value_depends_response_body():
    next_page_tokens = {"cursor": "{{ decoded_response['next_page_cursor'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"cursor": response_body["next_page_cursor"]}


def test_value_depends_response_header():
    next_page_tokens = {"cursor": "{{ headers['A_HEADER'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token["cursor"] == response.headers["A_HEADER"]


def test_value_depends_on_last_responses():
    next_page_tokens = {"cursor": "{{ last_records[-1]['id'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token["cursor"] == "0"


def test_name_is_interpolated():
    next_page_tokens = {"{{ decoded_response['next_page_cursor'] }}": "a_static_value"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {response_body["next_page_cursor"]: "a_static_value"}


def test_token_is_none_if_field_not_found():
    next_page_tokens = {"cursor": "{{ decoded_response['next_page_cursor'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, decoder, config)

    r = requests.Response()
    r._content = json.dumps({"not_next_page_cursor": "12345"}).encode("utf-8")

    next_page_token = paginator.next_page_token(r, last_responses)

    assert next_page_token is None

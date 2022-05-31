#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.declarative.response import Response

config = {"option": "OPTION"}

headers = {"A_HEADER": "HEADER_VALUE"}
body = {"next_page_cursor": "12345"}
response = Response(headers=headers, body=body)

last_responses = [{"id": 0}]


def test_value_is_static():
    next_page_tokens = {"cursor": "a_static_value"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"cursor": "a_static_value"}


def test_value_depends_response_body():
    next_page_tokens = {"cursor": "{{ decoded_response['next_page_cursor'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {"cursor": body["next_page_cursor"]}


def test_value_depends_response_header():
    next_page_tokens = {"cursor": "{{ headers['A_HEADER'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token["cursor"] == response.headers["A_HEADER"]


def test_value_depends_on_last_responses():
    next_page_tokens = {"cursor": "{{ last_records[-1]['id'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token["cursor"] == "0"


def test_name_is_interpolated():
    next_page_tokens = {"{{ decoded_response['next_page_cursor'] }}": "a_static_value"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    next_page_token = paginator.next_page_token(response, last_responses)

    assert next_page_token == {body["next_page_cursor"]: "a_static_value"}


def test_token_is_none_if_field_not_found():
    next_page_tokens = {"cursor": "{{ decoded_response['next_page_cursor'] }}"}
    paginator = InterpolatedPaginator(next_page_tokens, config)

    r = Response(body={"not_next_page_cursor": "12345"})

    next_page_token = paginator.next_page_token(r, last_responses)

    assert next_page_token is None

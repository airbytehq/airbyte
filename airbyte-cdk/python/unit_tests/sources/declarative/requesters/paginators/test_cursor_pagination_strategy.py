#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy


@pytest.mark.parametrize(
    "test_name, template_string, stop_condition, expected_token, page_size",
    [
        ("test_static_token", "token", None, "token", None),
        ("test_static_token_with_page_size", "token", None, "token", 5),
        ("test_token_from_config", "{{ config.config_key }}", None, "config_value", None),
        ("test_token_from_last_record", "{{ last_records[-1].id }}", None, 1, None),
        ("test_token_from_response", "{{ response._metadata.content }}", None, "content_value", None),
        ("test_token_from_parameters", "{{ parameters.key }}", None, "value", None),
        ("test_token_not_found", "{{ response.invalid_key }}", None, None, None),
        ("test_static_token_with_stop_condition_false", "token", InterpolatedBoolean("{{False}}", parameters={}), "token", None),
        ("test_static_token_with_stop_condition_true", "token", InterpolatedBoolean("{{True}}", parameters={}), None, None),
        (
            "test_token_from_header",
            "{{ headers.next }}",
            InterpolatedBoolean("{{ not headers.has_more }}", parameters={}),
            "ready_to_go",
            None,
        ),
        (
            "test_token_from_response_header_links",
            "{{ headers.link.next.url }}",
            InterpolatedBoolean("{{ not headers.link.next.url }}", parameters={}),
            "https://adventure.io/api/v1/records?page=2&per_page=100",
            None,
        ),
    ],
)
def test_cursor_pagination_strategy(test_name, template_string, stop_condition, expected_token, page_size):
    decoder = JsonDecoder(parameters={})
    config = {"config_key": "config_value"}
    parameters = {"key": "value"}
    strategy = CursorPaginationStrategy(
        page_size=page_size,
        cursor_value=template_string,
        config=config,
        stop_condition=stop_condition,
        decoder=decoder,
        parameters=parameters,
    )

    response = requests.Response()
    link_str = '<https://adventure.io/api/v1/records?page=2&per_page=100>; rel="next"'
    response.headers = {"has_more": True, "next": "ready_to_go", "link": link_str}
    response_body = {"_metadata": {"content": "content_value"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    token = strategy.next_page_token(response, last_records)
    assert expected_token == token
    assert page_size == strategy.get_page_size()

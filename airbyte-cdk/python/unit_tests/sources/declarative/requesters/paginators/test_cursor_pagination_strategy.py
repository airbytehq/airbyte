#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy


@pytest.mark.parametrize(
    "test_name, template_string, stop_condition, expected_token",
    [
        ("test_static_token", "token", None, "token"),
        ("test_token_from_config", "{{ config.config_key }}", None, "config_value"),
        ("test_token_from_last_record", "{{ last_records[-1].id }}", None, 1),
        ("test_token_from_response", "{{ response._metadata.content }}", None, "content_value"),
        ("test_token_from_options", "{{ options.key }}", None, "value"),
        ("test_token_not_found", "{{ response.invalid_key }}", None, None),
        ("test_static_token_with_stop_condition_false", "token", InterpolatedBoolean("{{False}}", options={}), "token"),
        ("test_static_token_with_stop_condition_true", "token", InterpolatedBoolean("{{True}}", options={}), None),
        ("test_token_from_header", "{{ headers.next }}", InterpolatedBoolean("{{ not headers.has_more }}", options={}), "ready_to_go"),
        (
            "test_token_from_response_header_links",
            "{{ headers.link.next.url }}",
            InterpolatedBoolean("{{ not headers.link.next.url }}", options={}),
            "https://adventure.io/api/v1/records?page=2&per_page=100",
        ),
    ],
)
def test_cursor_pagination_strategy(test_name, template_string, stop_condition, expected_token):
    decoder = JsonDecoder(options={})
    config = {"config_key": "config_value"}
    options = {"key": "value"}
    strategy = CursorPaginationStrategy(
        cursor_value=template_string, config=config, stop_condition=stop_condition, decoder=decoder, options=options
    )

    response = requests.Response()
    link_str = '<https://adventure.io/api/v1/records?page=2&per_page=100>; rel="next"'
    response.headers = {"has_more": True, "next": "ready_to_go", "link": link_str}
    response_body = {"_metadata": {"content": "content_value"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    token = strategy.next_page_token(response, last_records)
    assert expected_token == token

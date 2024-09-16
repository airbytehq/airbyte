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
    "template_string, stop_condition, expected_token, page_size",
    [
        ("token", None, "token", None),
        ("token", None, "token", 5),
        ("{{ config.config_key }}", None, "config_value", None),
        ("{{ last_record.id }}", None, 1, None),
        ("{{ response._metadata.content }}", None, "content_value", None),
        ("{{ parameters.key }}", None, "value", None),
        ("{{ response.invalid_key }}", None, None, None),
        ("token", InterpolatedBoolean("{{False}}", parameters={}), "token", None),
        ("token", InterpolatedBoolean("{{True}}", parameters={}), None, None),
        ("token", "{{True}}", None, None),
        (
            "{{ headers.next }}",
            InterpolatedBoolean("{{ not headers.has_more }}", parameters={}),
            "ready_to_go",
            None,
        ),
        (
            "{{ headers.link.next.url }}",
            InterpolatedBoolean("{{ not headers.link.next.url }}", parameters={}),
            "https://adventure.io/api/v1/records?page=2&per_page=100",
            None,
        ),
    ],
    ids=[
        "test_static_token",
        "test_static_token_with_page_size",
        "test_token_from_config",
        "test_token_from_last_record",
        "test_token_from_response",
        "test_token_from_parameters",
        "test_token_not_found",
        "test_static_token_with_stop_condition_false",
        "test_static_token_with_stop_condition_true",
        "test_static_token_with_string_stop_condition",
        "test_token_from_header",
        "test_token_from_response_header_links",
    ],
)
def test_cursor_pagination_strategy(template_string, stop_condition, expected_token, page_size):
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
    last_record = {"id": 1, "more_records": True}

    token = strategy.next_page_token(response, 1, last_record)
    assert expected_token == token
    assert page_size == strategy.get_page_size()


def test_last_record_points_to_the_last_item_in_last_records_array():
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]
    strategy = CursorPaginationStrategy(
        page_size=1,
        cursor_value="{{ last_record.id }}",
        config={},
        parameters={},
    )

    response = requests.Response()
    next_page_token = strategy.next_page_token(response, 2, last_records[-1])
    assert next_page_token == 1


def test_last_record_is_node_if_no_records():
    strategy = CursorPaginationStrategy(
        page_size=1,
        cursor_value="{{ last_record.id }}",
        config={},
        parameters={},
    )

    response = requests.Response()
    next_page_token = strategy.next_page_token(response, 0, None)
    assert next_page_token is None


def test_reset_with_initial_token():
    strategy = CursorPaginationStrategy(
        page_size=10,
        cursor_value="{{ response.next_page }}",
        config={},
        parameters={},
    )

    assert strategy.initial_token is None

    strategy.reset("https://for-all-mankind.nasa.com/api/v1/astronauts")

    assert strategy.initial_token == "https://for-all-mankind.nasa.com/api/v1/astronauts"

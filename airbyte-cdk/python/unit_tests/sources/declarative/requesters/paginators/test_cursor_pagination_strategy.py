#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.requesters.paginators.cursor_pagination_strategy import CursorPaginationStrategy


@pytest.mark.parametrize(
    "test_name, template_string, expected_token",
    [
        ("test_static_token", "token", "token"),
        ("test_token_from_config", "{{ config.config_key }}", "config_value"),
        ("test_token_from_last_record", "{{ last_records[-1].id }}", 1),
        ("test_token_from_decoded_response", "{{ decoded_response._metadata.content }}", "content_value"),
        ("test_token_not_found", "{{ decoded_response.invalid_key }}", None),
    ],
)
def test_interpolated_pagination_strategy(test_name, template_string, expected_token):
    decoder = JsonDecoder()
    config = {"config_key": "config_value"}
    strategy = CursorPaginationStrategy(template_string, config, decoder)

    response = requests.Response()
    response.headers = {"has_more": True}
    response_body = {"_metadata": {"content": "content_value"}, "accounts": [], "end": 99, "total": 200, "characters": {}}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0, "more_records": True}, {"id": 1, "more_records": True}]

    token = strategy.next_page_token(response, last_records)
    assert expected_token == token

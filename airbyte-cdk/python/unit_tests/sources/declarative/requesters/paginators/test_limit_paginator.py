#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.limit_paginator import LimitPaginator, RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy


@pytest.mark.parametrize(
    "test_name, page_token_request_option, stop_condition, expected_updated_path, expected_request_params, expected_headers, expected_body_data, expected_body_json, last_records, expected_next_page_token",
    [
        (
            "test_limit_paginator_path",
            RequestOption(inject_into=RequestOptionType.path, options={}),
            None,
            "/next_url",
            {"limit": 2},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
        ),
        (
            "test_limit_paginator_request_param",
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
            None,
            None,
            {"limit": 2, "from": "https://airbyte.io/next_url"},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
        ),
        (
            "test_limit_paginator_no_token",
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
            InterpolatedBoolean(condition="{{True}}", options={}),
            None,
            {"limit": 2},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            None,
        ),
        (
            "test_limit_paginator_cursor_header",
            RequestOption(inject_into=RequestOptionType.header, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {"from": "https://airbyte.io/next_url"},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
        ),
        (
            "test_limit_paginator_cursor_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {},
            {"from": "https://airbyte.io/next_url"},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
        ),
        (
            "test_limit_paginator_cursor_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {},
            {},
            {"from": "https://airbyte.io/next_url"},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
        ),
    ],
)
def test_limit_paginator(
    test_name,
    page_token_request_option,
    stop_condition,
    expected_updated_path,
    expected_request_params,
    expected_headers,
    expected_body_data,
    expected_body_json,
    last_records,
    expected_next_page_token,
):
    limit_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", options={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    options = {}
    strategy = CursorPaginationStrategy(
        cursor_value=cursor_value, stop_condition=stop_condition, decoder=JsonDecoder(options={}), config=config, options=options
    )
    paginator = LimitPaginator(
        page_size=2,
        limit_option=limit_request_option,
        page_token_option=page_token_request_option,
        pagination_strategy=strategy,
        config=config,
        url_base=url_base,
        options={},
    )

    response = requests.Response()
    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")

    actual_next_page_token = paginator.next_page_token(response, last_records)
    actual_next_path = paginator.path()
    actual_request_params = paginator.get_request_params()
    actual_headers = paginator.get_request_headers()
    actual_body_data = paginator.get_request_body_data()
    actual_body_json = paginator.get_request_body_json()
    assert actual_next_page_token == expected_next_page_token
    assert actual_next_path == expected_updated_path
    assert actual_request_params == expected_request_params
    assert actual_headers == expected_headers
    assert actual_body_data == expected_body_data
    assert actual_body_json == expected_body_json


def test_limit_cannot_be_set_in_path():
    limit_request_option = RequestOption(inject_into=RequestOptionType.path, options={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", options={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    options = {}
    strategy = CursorPaginationStrategy(cursor_value=cursor_value, config=config, options=options)
    try:
        LimitPaginator(
            page_size=2,
            limit_option=limit_request_option,
            page_token_option=page_token_request_option,
            pagination_strategy=strategy,
            config=config,
            url_base=url_base,
            options={},
        )
        assert False
    except ValueError:
        pass


def test_reset():
    limit_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", options={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", options={})
    url_base = "https://airbyte.io"
    config = {}
    strategy = MagicMock()
    LimitPaginator(2, limit_request_option, page_token_request_option, strategy, config, url_base, options={}).reset()
    assert strategy.reset.called

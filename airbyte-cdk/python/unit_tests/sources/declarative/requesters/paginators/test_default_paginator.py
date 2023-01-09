#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import DefaultPaginator, RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy


@pytest.mark.parametrize(
    "test_name, page_token_request_option, stop_condition, expected_updated_path, expected_request_params, expected_headers, expected_body_data, expected_body_json, last_records, expected_next_page_token, limit",
    [
        (
            "test_default_paginator_path",
            RequestOption(inject_into=RequestOptionType.path, options={}),
            None,
            "/next_url",
            {"limit": 2},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
            2,
        ),
        (
            "test_default_paginator_request_param",
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
            None,
            None,
            {"limit": 2, "from": "https://airbyte.io/next_url"},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
            2,
        ),
        (
            "test_default_paginator_no_token",
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", options={}),
            InterpolatedBoolean(condition="{{True}}", options={}),
            None,
            {"limit": 2},
            {},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            None,
            2,
        ),
        (
            "test_default_paginator_cursor_header",
            RequestOption(inject_into=RequestOptionType.header, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {"from": "https://airbyte.io/next_url"},
            {},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
            2,
        ),
        (
            "test_default_paginator_cursor_body_data",
            RequestOption(inject_into=RequestOptionType.body_data, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {},
            {"from": "https://airbyte.io/next_url"},
            {},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
            2,
        ),
        (
            "test_default_paginator_cursor_body_json",
            RequestOption(inject_into=RequestOptionType.body_json, field_name="from", options={}),
            None,
            None,
            {"limit": 2},
            {},
            {},
            {"from": "https://airbyte.io/next_url"},
            [{"id": 0}, {"id": 1}],
            {"next_page_token": "https://airbyte.io/next_url"},
            2,
        ),
    ],
)
def test_default_paginator_with_cursor(
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
    limit,
):
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", options={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    options = {}
    strategy = CursorPaginationStrategy(
        page_size=limit,
        cursor_value=cursor_value,
        stop_condition=stop_condition,
        decoder=JsonDecoder(options={}),
        config=config,
        options=options,
    )
    paginator = DefaultPaginator(
        page_size_option=page_size_request_option,
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
    page_size_request_option = RequestOption(inject_into=RequestOptionType.path, options={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", options={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    options = {}
    strategy = CursorPaginationStrategy(page_size=5, cursor_value=cursor_value, config=config, options=options)
    try:
        DefaultPaginator(
            page_size_option=page_size_request_option,
            page_token_option=page_token_request_option,
            pagination_strategy=strategy,
            config=config,
            url_base=url_base,
            options={},
        )
        assert False
    except ValueError:
        pass


def test_page_size_option_cannot_be_set_if_strategy_has_no_limit():
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="page_size", options={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", options={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    options = {}
    strategy = CursorPaginationStrategy(page_size=None, cursor_value=cursor_value, config=config, options=options)
    try:
        DefaultPaginator(
            page_size_option=page_size_request_option,
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
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", options={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", options={})
    url_base = "https://airbyte.io"
    config = {}
    strategy = MagicMock()
    DefaultPaginator(strategy, config, url_base, options={}, page_size_option=page_size_request_option, page_token_option=page_token_request_option).reset()
    assert strategy.reset.called

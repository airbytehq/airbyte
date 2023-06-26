#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import (
    DefaultPaginator,
    PaginatorTestReadDecorator,
    RequestOption,
    RequestOptionType,
)
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath


@pytest.mark.parametrize(
    "test_name, page_token_request_option, stop_condition, expected_updated_path, expected_request_params, expected_headers, expected_body_data, expected_body_json, last_records, expected_next_page_token, limit",
    [
        (
            "test_default_paginator_path",
            RequestPath(parameters={}),
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
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", parameters={}),
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
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="from", parameters={}),
            InterpolatedBoolean(condition="{{True}}", parameters={}),
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
            RequestOption(inject_into=RequestOptionType.header, field_name="from", parameters={}),
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
            RequestOption(inject_into=RequestOptionType.body_data, field_name="from", parameters={}),
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
            RequestOption(inject_into=RequestOptionType.body_json, field_name="from", parameters={}),
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
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", parameters={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    parameters = {}
    strategy = CursorPaginationStrategy(
        page_size=limit,
        cursor_value=cursor_value,
        stop_condition=stop_condition,
        decoder=JsonDecoder(parameters={}),
        config=config,
        parameters=parameters,
    )
    paginator = DefaultPaginator(
        page_size_option=page_size_request_option,
        page_token_option=page_token_request_option,
        pagination_strategy=strategy,
        config=config,
        url_base=url_base,
        parameters={},
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


def test_page_size_option_cannot_be_set_if_strategy_has_no_limit():
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="page_size", parameters={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", parameters={})
    cursor_value = "{{ response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    parameters = {}
    strategy = CursorPaginationStrategy(page_size=None, cursor_value=cursor_value, config=config, parameters=parameters)
    try:
        DefaultPaginator(
            page_size_option=page_size_request_option,
            page_token_option=page_token_request_option,
            pagination_strategy=strategy,
            config=config,
            url_base=url_base,
            parameters={},
        )
        assert False
    except ValueError:
        pass


def test_reset():
    page_size_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="limit", parameters={})
    page_token_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, field_name="offset", parameters={})
    url_base = "https://airbyte.io"
    config = {}
    strategy = OffsetIncrement(config={}, page_size=2, parameters={})
    paginator = DefaultPaginator(
        strategy, config, url_base, parameters={}, page_size_option=page_size_request_option, page_token_option=page_token_request_option
    )
    initial_request_parameters = paginator.get_request_params()
    paginator.next_page_token(MagicMock(), [{"first key": "first value"}, {"second key": "second value"}])
    request_parameters_for_second_request = paginator.get_request_params()
    paginator.reset()
    request_parameters_after_reset = paginator.get_request_params()
    assert initial_request_parameters == request_parameters_after_reset
    assert request_parameters_for_second_request != request_parameters_after_reset


def test_limit_page_fetched():
    maximum_number_of_pages = 5
    number_of_next_performed = maximum_number_of_pages - 1
    paginator = PaginatorTestReadDecorator(
        DefaultPaginator(
            page_size_option=MagicMock(),
            page_token_option=MagicMock(),
            pagination_strategy=MagicMock(),
            config=MagicMock(),
            url_base=MagicMock(),
            parameters={},
        ),
        maximum_number_of_pages,
    )

    for _ in range(number_of_next_performed):
        last_token = paginator.next_page_token(MagicMock(), MagicMock())
        assert last_token

    assert not paginator.next_page_token(MagicMock(), MagicMock())


def test_paginator_with_page_option_no_page_size():
    pagination_strategy = OffsetIncrement(config={}, page_size=None, parameters={})

    with pytest.raises(ValueError):
        DefaultPaginator(
            page_size_option=MagicMock(),
            page_token_option=RequestOption("limit", RequestOptionType.request_parameter, parameters={}),
            pagination_strategy=pagination_strategy,
            config=MagicMock(),
            url_base=MagicMock(),
            parameters={},
        ),

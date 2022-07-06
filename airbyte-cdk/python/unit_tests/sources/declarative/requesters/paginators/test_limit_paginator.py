#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.paginators.cursor_pagination_strategy import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.limit_paginator import LimitPaginator, RequestOption, RequestOptionType


@pytest.mark.parametrize(
    "test_name, page_token_request_option, expected_updated_path, expected_request_params, expected_headers, expected_body_data, expected_body_json",
    [
        ("test_limit_paginator_cursor_param", RequestOption(option_type=RequestOptionType.path), "/next_url", {"limit": 2}, {}, {}, {}),
        (
            "test_limit_paginator_cursor_param",
            RequestOption(option_type=RequestOptionType.request_parameter, field_name="from"),
            None,
            {"limit": 2, "from": "https://airbyte.io/next_url"},
            {},
            {},
            {},
        ),
        (
            "test_limit_paginator_cursor_header",
            RequestOption(option_type=RequestOptionType.header, field_name="from"),
            None,
            {"limit": 2},
            {"from": "https://airbyte.io/next_url"},
            {},
            {},
        ),
        (
            "test_limit_paginator_cursor_body_data",
            RequestOption(option_type=RequestOptionType.body_data, field_name="from"),
            None,
            {"limit": 2},
            {},
            {"from": "https://airbyte.io/next_url"},
            {},
        ),
        (
            "test_limit_paginator_cursor_body_json",
            RequestOption(option_type=RequestOptionType.body_json, field_name="from"),
            None,
            {"limit": 2},
            {},
            {},
            {"from": "https://airbyte.io/next_url"},
        ),
    ],
)
def test_limit_paginator_update_path(
    test_name,
    page_token_request_option,
    expected_updated_path,
    expected_request_params,
    expected_headers,
    expected_body_data,
    expected_body_json,
):
    limit_request_option = RequestOption(option_type=RequestOptionType.request_parameter, field_name="limit")
    cursor_value = "{{ decoded_response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    strategy = CursorPaginationStrategy(cursor_value, config)
    paginator = LimitPaginator(2, limit_request_option, page_token_request_option, strategy, config, url_base)

    response = requests.Response()
    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")

    last_records = [{"id": 0}, {"id": 1}]
    actual_next_page_token = paginator.next_page_token(response, last_records)
    actual_next_path = paginator.path()
    actual_request_params = paginator.request_params()
    actual_headers = paginator.request_headers()
    actual_body_data = paginator.request_body_data()
    actual_body_json = paginator.request_body_json()
    assert actual_next_page_token == {"next_page_token": "https://airbyte.io/next_url"}
    assert actual_next_path == expected_updated_path
    assert actual_request_params == expected_request_params
    assert actual_headers == expected_headers
    assert actual_body_data == expected_body_data
    assert actual_body_json == expected_body_json


@pytest.mark.parametrize(
    "test_name",
    [
        ("test_limit_options"),
    ],
)
def test_limit_cannot_be_set_in_path(test_name):
    limit_request_option = RequestOption(option_type=RequestOptionType.path)
    page_token_request_option = RequestOption(option_type=RequestOptionType.request_parameter, field_name="offset")
    cursor_value = "{{ decoded_response.next }}"
    url_base = "https://airbyte.io"
    config = {}
    strategy = CursorPaginationStrategy(cursor_value, config)
    try:
        LimitPaginator(2, limit_request_option, page_token_request_option, strategy, config, url_base)
        assert False
    except ValueError:
        pass

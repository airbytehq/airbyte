#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


@pytest.mark.parametrize(
    "page_size, start_from, last_records, expected_next_page_token, expected_offset",
    [
        pytest.param(2, 1, [{"id": 0}, {"id": 1}], 2, 2, id="test_same_page_size_start_from_0"),
        pytest.param(3, 1, [{"id": 0}, {"id": 1}], None, 1, id="test_larger_page_size_start_from_0"),
        pytest.param(2, 0, [{"id": 0}, {"id": 1}], 1, 1, id="test_same_page_size_start_from_1"),
        pytest.param(3, 0, [{"id": 0}, {"id": 1}], None, 0, id="test_larger_page_size_start_from_0"),
        pytest.param(None, 0, [], None, 0, id="test_no_page_size"),
    ],
)
def test_page_increment_paginator_strategy(page_size, start_from, last_records, expected_next_page_token, expected_offset):
    paginator_strategy = PageIncrement(page_size, parameters={}, start_from_page=start_from)
    assert paginator_strategy._page == start_from

    response = requests.Response()

    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")

    next_page_token = paginator_strategy.next_page_token(response, last_records)
    assert expected_next_page_token == next_page_token
    assert expected_offset == paginator_strategy._page

    paginator_strategy.reset()
    assert start_from == paginator_strategy._page

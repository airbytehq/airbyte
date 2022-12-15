#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


@pytest.mark.parametrize(
    "test_name, page_size, start_from, expected_next_page_token, expected_offset",
    [
        ("test_same_page_size_start_from_0", 2, 1, 2, 2),
        ("test_larger_page_size_start_from_0", 3, 1, None, 1),
        ("test_same_page_size_start_from_1", 2, 0, 1, 1),
        ("test_larger_page_size_start_from_0", 3, 0, None, 0)
    ],
)
def test_page_increment_paginator_strategy(test_name, page_size, start_from, expected_next_page_token, expected_offset):
    paginator_strategy = PageIncrement(page_size, options={}, start_from_page=start_from)
    assert paginator_strategy._page == start_from

    response = requests.Response()

    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0}, {"id": 1}]

    next_page_token = paginator_strategy.next_page_token(response, last_records)
    assert expected_next_page_token == next_page_token
    assert expected_offset == paginator_strategy._page

    paginator_strategy.reset()
    assert start_from == paginator_strategy._page

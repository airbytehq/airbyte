#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.offset_increment import OffsetIncrement


@pytest.mark.parametrize(
    "test_name, page_size, expected_next_page_token, expected_offset",
    [
        ("test_same_page_size", 2, 2, 2),
        ("test_larger_page_size", 3, None, 0),
    ],
)
def test_offset_increment_paginator_strategy(test_name, page_size, expected_next_page_token, expected_offset):
    paginator_strategy = OffsetIncrement(page_size, options={})
    assert paginator_strategy._offset == 0

    response = requests.Response()

    response.headers = {"A_HEADER": "HEADER_VALUE"}
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")
    last_records = [{"id": 0}, {"id": 1}]

    next_page_token = paginator_strategy.next_page_token(response, last_records)
    assert expected_next_page_token == next_page_token
    assert expected_offset == paginator_strategy._offset

    paginator_strategy.reset()
    assert 0 == paginator_strategy._offset
